import json
import os
import csv
import nltk
from nltk.corpus import stopwords, words
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from nltk.metrics import edit_distance
from pathlib import Path

# Ensure necessary NLTK data is downloaded
nltk.download("punkt", quiet=True)
nltk.download("stopwords", quiet=True)
nltk.download("wordnet", quiet=True)
nltk.download("words", quiet=True)



absolute_path = Path(__file__).resolve();

# Paths to the required files
output_dir = os.path.join(absolute_path.parents[1],"inverted_index" ,"barrels")
lexicon_path = os.path.join(absolute_path.parents[1] , "Preprocessing", "lexicon.csv")


# Load the lexicon file into a dictionary
def load_lexicon():
    lexicon = {}
    with open(lexicon_path, "r") as file:
        reader = csv.reader(file)
        for row in reader:
            word, term_id = row
            lexicon[word] = term_id
    return lexicon

# Initialize NLTK tools
stop_words = set(stopwords.words("english"))
lemmatizer = WordNetLemmatizer()
english_words = set(words.words())  # Set of English words for filtering

# Function to process the query (lemmatization and stopword removal)
def process_query(query):
    query_tokens = word_tokenize(query.lower())  # Tokenize and lowercase the query
    query_tokens = [
        lemmatizer.lemmatize(token) for token in query_tokens
        if len(token) > 2 and token not in stop_words  # Modified to allow more flexibility
    ]
    return query_tokens  # Return the list of lemmatized query words

# Function to determine which barrel a term belongs to (based on term ID)
def get_barrel(term_id):
    try:
        term_int = int(term_id)
        barrel_key = term_int // 100
        return str(barrel_key)
    except ValueError:
        return None

# Function to determine which bucket within the barrel the term belongs to
def get_bucket(term_id):
    try:
        term_int = int(term_id)
        bucket_key = term_int % 10
        return str(bucket_key)
    except ValueError:
        return None

# Function to find the closest matching word from the lexicon using Levenshtein distance
def find_closest_word(query_word, lexicon):
    closest_word = None
    min_distance = float('inf')
    for word in lexicon:
        dist = edit_distance(query_word, word)
        if dist < min_distance:
            closest_word = word
            min_distance = dist
    return closest_word

# Function to perform multi-word search (all words must be present in the same document)
def multi_word_search(query, lexicon):
    lemmatized_words = process_query(query)

    if not lemmatized_words:
        return f"Invalid query: '{query}'. Could not lemmatize or process the words."

    # Dictionary to hold postings for each query word
    word_postings = {}

    # Collect postings for each lemmatized word
    for word in lemmatized_words:
        term_id = lexicon.get(word)
        if not term_id:
            # Try finding the closest match if no exact match is found
            closest_word = find_closest_word(word, lexicon)
            if closest_word:
                print(f"Warning: No exact match found for '{word}'. Using closest match: '{closest_word}'")
                term_id = lexicon.get(closest_word)
            else:
                return f"Word '{word}' or any close match not found in the lexicon."

        barrel_key = get_barrel(term_id)
        bucket_key = get_bucket(term_id)

        barrel_path = os.path.join(output_dir, f"{barrel_key}.json")
        if not os.path.exists(barrel_path):
            return f"No barrel found for word '{word}' (term ID: {term_id})."

        with open(barrel_path, "r") as file:
            barrel_data = json.load(file)

        # Get postings from the relevant bucket
        postings = barrel_data.get(bucket_key, {}).get(term_id, [])
        word_postings[word] = postings

    # Find documents that contain all query words
    doc_results = {}

    # Loop through each word's postings and collect the relevant documents
    for word, postings in word_postings.items():
        for posting in postings:
            doc_id = posting["docID"]
            if doc_id not in doc_results:
                doc_results[doc_id] = {}

            doc_results[doc_id][word] = {
                "frequency": posting["frequency"],
                "positions": posting["positions"]
            }

    # Filter documents that contain *all* query words
    final_results = {}
    for doc_id, terms in doc_results.items():
        if all(word in terms for word in lemmatized_words):
            final_results[doc_id] = terms

    # Store the results in a JSON file
    results_path = os.path.join(absolute_path.parents[1],"Ranking" ,"filtered_results.json")

    with open(results_path, "w") as result_file:
        json.dump(final_results, result_file, indent=4)

    if final_results:
        return f"Results for multi-word query '{query}' have been stored in '{results_path}'."
    else:
        return f"No documents found containing all words from the query: {query}."

# Main Execution
if __name__ == "__main__":
    lexicon = load_lexicon()
    query = input("Enter a multiple-word query to search: ").strip()
    result = multi_word_search(query, lexicon)
    print(result)