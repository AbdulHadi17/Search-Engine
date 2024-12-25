import sys
from pathlib import Path

# Add the parent directory of `search` and `Ranking` to sys.path
sys.path.append(str(Path(__file__).resolve().parent.parent / "search"))
sys.path.append(str(Path(__file__).resolve().parent.parent / "Ranking"))

# Now import modules
from singleSearch import SingleWordSearch
from multiSearch import MultiWordSearch
from ranking import DocumentRankingUtility




def determine_query_type(query):
    """
    Determines whether a query is a single word or multiple words.

    Parameters:
        query (str): The search query from the frontend.

    Returns:
        str: 'single' if the query contains a single word, 'multi' otherwise.
    """
    if len(query.split()) == 1:
        return 'single'
    else:
        return 'multi'

def main():
    """
    Main function to handle query and execute appropriate classes.
    """
    # Get the query from the frontend (replace with actual query fetching mechanism)
    query = input("Enter your query: ")  # Simulating frontend input

    if not query.strip():
        print("Error: Query cannot be empty.")
        sys.exit(1)

    query_type = determine_query_type(query)

    try:
        # Run the appropriate class-based search based on query type
        if query_type == 'single':
            print(f"Running SingleWordSearch with query: {query}")
            search_instance = SingleWordSearch(query)
            result = search_instance.search()
        else:
            print(f"Running MultiWordSearch with query: {query}")
            search_instance = MultiWordSearch(query)
            result = search_instance.search()

        # Print the search result
        print("Search result:", result)

        # Perform ranking if search was successful
        if result and "filtered_results.json" in result:
            print("Performing ranking...")
            absolute_path = Path(__file__).resolve()
            filtered_result_path = absolute_path.parents[1] / 'Ranking' / 'filtered_results.json'
            metadata_file_path = absolute_path.parents[1] / 'data' / 'postings.csv'

            ranking_utility = DocumentRankingUtility(filtered_result_path, metadata_file_path)
            ranked_results = ranking_utility.rank()

            print("Ranked results:")
            for ranked_result in ranked_results:
                print(ranked_result)

    except Exception as e:
        print(f"An error occurred while running search or ranking: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
