import json
import pandas as pd
from pathlib import Path

class DocumentRankingUtility:
    def __init__(self, filtered_results_path, metadata_file_path):
        self.filtered_results_path = filtered_results_path
        self.metadata_file_path = metadata_file_path

    def reformat_filtered_results(self, filtered_results):
        """
        Reformat filtered results to ensure it follows the correct format.

        Parameters:
            filtered_results (dict or list): Raw filtered results from JSON.

        Returns:
            list: Reformatted filtered results in the desired list format.
        """
        if isinstance(filtered_results, dict):  # Convert dict format to list
            reformatted_results = []
            for doc_id, terms in filtered_results.items():
                if not isinstance(terms, dict):
                    raise ValueError(f"Invalid terms format for doc_id {doc_id}: {terms}")

                consolidated_entry = {
                    "docID": doc_id,
                    "frequency": sum(
                        term.get("frequency", 0) for term in terms.values()
                        if isinstance(term, dict)
                    ),
                    "positions": sorted(
                        pos for term in terms.values() if isinstance(term, dict)
                        for pos in term.get("positions", [])
                    ),
                }
                reformatted_results.append(consolidated_entry)
            return reformatted_results
        elif isinstance(filtered_results, list):  # Already in list format
            for item in filtered_results:
                if not all(key in item for key in ("docID", "frequency", "positions")):
                    raise ValueError(f"Invalid item format in filtered results: {item}")
            return filtered_results
        else:
            raise ValueError("Unexpected format for filtered results.")

    def rank_documents_with_metadata(self, filtered_results, metadata_df):
        """
        Rank documents based on relevance using frequency and positions,
        and return specific fields in the output.

        Parameters:
            filtered_results (list): List of documents with frequencies and positions.
            metadata_df (DataFrame): Metadata DataFrame for each document.

        Returns:
            list: Ranked list of documents with required fields.
        """
        scores = {}

        for result in filtered_results:
            doc_id = int(result["docID"])  # Convert docID to integer for indexing
            frequency = result["frequency"]
            positions = result["positions"]

            # Calculate average position
            avg_position = sum(positions) / len(positions) if positions else float("inf")

            # Calculate score
            score = 0.7 * frequency + 0.3 * (1 / avg_position)
            scores[doc_id] = score

        # Sort documents by score
        ranked_docs = sorted(scores.items(), key=lambda x: x[1], reverse=True)

        # Prepare the results with only required fields
        results = []
        for doc_id, score in ranked_docs:
            # Retrieve the nth row based on doc_id
            if 0 <= doc_id < len(metadata_df):  # Ensure doc_id is within range
                row = metadata_df.iloc[doc_id]
                title = row.get("title", "N/A")
                url = row.get("job_posting_url", "N/A")
            else:
                title = "N/A"
                url = "N/A"

            results.append({
                "doc_id": doc_id,
                "score": score,
                "title": title,
                "url": url
            })

        return results

    def load_filtered_results(self):
        try:
            if self.filtered_results_path.exists():
                with open(self.filtered_results_path, mode='r', encoding='utf-8') as file:
                    filtered_results = json.load(file)
                    return self.reformat_filtered_results(filtered_results)
            else:
                raise FileNotFoundError("Filtered results JSON file not found.")
        except Exception as e:
            print(f"Error reading filtered results file: {e}")
            return []  # Fallback to empty list if JSON is missing or invalid

    def load_metadata(self, columns_to_process):
        try:
            if self.metadata_file_path.exists():
                metadata_df = pd.read_csv(self.metadata_file_path, usecols=columns_to_process)

                # Validate metadata DataFrame
                if not all(col in metadata_df.columns for col in columns_to_process):
                    raise ValueError("Metadata file does not contain all required columns.")
                return metadata_df
            else:
                raise FileNotFoundError("Metadata CSV file not found.")
        except Exception as e:
            print(f"Error reading metadata file: {e}")
            return pd.DataFrame(columns=columns_to_process)  # Empty DataFrame if CSV not found

    def rank(self):
        columns_to_process = ["company_name", "description", "title", "location", "skills_desc", "job_posting_url"]

        # Load data
        filtered_results = self.load_filtered_results()
        metadata_df = self.load_metadata(columns_to_process)

        if filtered_results and not metadata_df.empty:
            ranked_results = self.rank_documents_with_metadata(filtered_results, metadata_df)
            return ranked_results
        else:
            print("No data available for ranking.")
            return []

# Example usage
if __name__ == "__main__":
    absolute_path = Path(__file__).resolve()
    filtered_result_path = absolute_path.parents[0] / 'filtered_results.json'
    metadata_file_path = absolute_path.parents[1] / 'data' / 'postings.csv'

    utility = DocumentRankingUtility(filtered_result_path, metadata_file_path)
    ranked_results = utility.rank()

    for result in ranked_results:
        print(json.dumps(result, indent=4))