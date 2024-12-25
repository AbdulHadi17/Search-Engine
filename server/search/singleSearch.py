import json
import os
import csv
import nltk
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from nltk import pos_tag
import difflib  # For fuzzy matching
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
lemmatizer = WordNetLemmatizer()

# Map NLTK POS tags to WordNet POS tags
def get_wordnet_pos(treebank_tag):
    if treebank_tag.startswith('J'):  # Adjective
        return 'a'
    elif treebank_tag.startswith('V'):  # Verb
        return 'v'
    elif treebank_tag.startswith('N'):  # Noun
        return 'n'
    elif treebank_tag.startswith('R'):  # Adverb
        return 'r'
    else:
        return None

# Function to process the query and lemmatize the word
def process_query(query):
    query_tokens = word_tokenize(query.lower())  # Tokenize and lowercase the query
    print(f"Tokenized query: {query_tokens}")  # Debug log for tokenized query

    # Filter out short tokens and any non-alphabetic tokens
    filtered_tokens = [token for token in query_tokens if len(token) > 2 and token.isalpha()]

    # Debug log for filtered tokens
    print(f"Filtered tokens: {filtered_tokens}")

    # Perform POS tagging and lemmatization
    pos_tags = pos_tag(filtered_tokens)
    lemmatized_tokens = []
    for word, tag in pos_tags:
        wordnet_pos = get_wordnet_pos(tag) or 'n'  # Default to noun if no match
        lemmatized_tokens.append(lemmatizer.lemmatize(word, pos=wordnet_pos))

    # Debug log to see what lemmatized tokens we have
    print(f"Lemmatized tokens: {lemmatized_tokens}")

    return lemmatized_tokens  # Return the list of lemmatized tokens

# Function to find the closest match in the lexicon (fuzzy matching)
def get_closest_match(query, lexicon):
    closest_match = difflib.get_close_matches(query, lexicon.keys(), n=1, cutoff=0.8)  # You can adjust cutoff for match quality
    return closest_match[0] if closest_match else None

# Function to determine which barrel a term belongs to (based on term ID)
def get_barrel(term_id):
    try:
        term_int = int(term_id)  # Convert the term to an integer
        barrel_key = term_int // 100  # Divide by 100 to get the barrel key
        return str(barrel_key)  # Return the barrel as a string
    except ValueError:
        return None  # Handle non-integer terms (if any)

# Function to determine which bucket within the barrel the term belongs to
def get_bucket(term_id):
    try:
        term_int = int(term_id)  # Convert the term to an integer
        bucket_key = term_int % 10  # Divide by 10 to determine the bucket key (0-9)
        return str(bucket_key)  # Return the bucket as a string
    except ValueError:
        return None  # Handle non-integer terms (if any)

def single_word_search(query, lexicon):
    # Process the query (lemmatize the word)
    lemmatized_query = process_query(query)

    if not lemmatized_query:
        return f"Invalid query: '{query}'. Could not lemmatize or process the word."

    # Use the first lemmatized token for searching
    lemmatized_word = lemmatized_query[0]

    # Search for the root word in the lexicon
    term_id = lexicon.get(lemmatized_word)

    # If the word is not found, try to find the closest match in the lexicon
    if not term_id:
        closest_match = get_closest_match(lemmatized_word, lexicon)
        if closest_match:
            print(f"Word '{lemmatized_word}' not found. Using closest match: '{closest_match}'")
            term_id = lexicon.get(closest_match)
        else:
            return f"Word '{lemmatized_word}' (and closest matches) not found in the lexicon."

    barrel_key = get_barrel(term_id)
    if not barrel_key:
        return f"Invalid term ID '{term_id}' for query: {query}. Unable to determine barrel."

    bucket_key = get_bucket(term_id)
    if not bucket_key:
        return f"Invalid term ID '{term_id}' for query: {query}. Unable to determine bucket."

    # Path to the appropriate barrel file
    barrel_path = os.path.join(output_dir, f"{barrel_key}.json")
    print(barrel_path)
    if not os.path.exists(barrel_path):
        return f"No results found for query: {query} (lemmatized as '{lemmatized_word}', term ID: {term_id})"

    # Load the barrel and search within the bucket
    with open(barrel_path, "r") as file:
        barrel_data = json.load(file)

    # Search for the term in the appropriate bucket
    postings = barrel_data.get(bucket_key, {}).get(term_id, None)
    if postings:
        # Path to store the results
        results_path = os.path.join(absolute_path.parents[1],"Ranking" ,"filtered_results.json")

        # Write results to the JSON file
        with open(results_path, "w") as result_file:
            json.dump(postings, result_file, indent=4)

        return f"Results for '{query}' (lemmatized as '{lemmatized_word}') have been stored in '{results_path}'."
    else:
        return f"No results found for query: {query} (lemmatized as '{lemmatized_word}', term ID: {term_id})"

# Main Execution
if __name__ == "__main__":
    lexicon = load_lexicon()  # Load the lexicon into memory
    query = input("Enter a single word to search: ").strip()
    result = single_word_search(query, lexicon)
    print(result)