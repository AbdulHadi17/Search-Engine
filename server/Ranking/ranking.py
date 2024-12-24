import json
import pandas as pd
from pathlib import Path


def reformat_filtered_results(filtered_results):
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
            consolidated_entry = {
                "docID": doc_id,
                "frequency": sum(term["frequency"] for term in terms),
                "positions": sorted(
                    pos for term in terms for pos in term["positions"]
                ),
            }
            reformatted_results.append(consolidated_entry)
        return reformatted_results
    elif isinstance(filtered_results, list):  # Already in list format
        return filtered_results
    else:
        raise ValueError("Unexpected format for filtered results.")


def rank_documents_with_metadata(filtered_results, metadata_df):
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


# Define file paths
absolute_path = Path(__file__).resolve()
filtered_result_path = absolute_path.parents[0] / 'filtered_results.json'
metadata_file_path = absolute_path.parents[1] / 'data' / 'postings.csv'

# Attempt to load filtered results
try:
    if filtered_result_path.exists():
        with open(filtered_result_path, mode='r', encoding='utf-8') as file:
            filtered_results = json.load(file)
            filtered_results = reformat_filtered_results(filtered_results)
    else:
        raise FileNotFoundError("Filtered results JSON file not found.")
except Exception as e:
    print(f"Error reading filtered results file: {e}")
    filtered_results = []  # Fallback to empty list if JSON is missing or invalid

# Define columns to process from metadata
columns_to_process = ["company_name", "description", "title", "location", "skills_desc", "job_posting_url"]

# Attempt to load metadata from CSV
try:
    if metadata_file_path.exists():
        metadata_df = pd.read_csv(metadata_file_path, usecols=columns_to_process)
    else:
        raise FileNotFoundError("Metadata CSV file not found.")
except Exception as e:
    print(f"Error reading metadata file: {e}")
    metadata_df = pd.DataFrame(columns=columns_to_process)  # Empty DataFrame if CSV not found

# Rank documents
if filtered_results and not metadata_df.empty:
    ranked_results = rank_documents_with_metadata(filtered_results, metadata_df)

    # Print ranked results
    for result in ranked_results:
        print(json.dumps(result, indent=4))
else:
    print("No data available for ranking.")
