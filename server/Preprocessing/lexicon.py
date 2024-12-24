import pandas as pd
import re
import nltk
from collections import Counter
from nltk.corpus import stopwords, words
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from pathlib import Path

def generate_lexicon(input_csv, output_csv="dummy_lexicon.csv"):
    """
    Processes the input CSV to generate vocabulary and appends unique entries 
    to a dummy lexicon file in the Preprocessing folder, with indices.
    
    Parameters:
        input_csv (str): Path to the input CSV file.
        output_csv (str): Name of the output dummy lexicon file (default: 'dummy_lexicon.csv').
    """
    # Ensure necessary NLTK data is downloaded
    nltk.download("punkt", quiet=True)
    nltk.download("stopwords", quiet=True)
    nltk.download("wordnet", quiet=True)
    nltk.download("words", quiet=True)

    # Define a set of English words
    english_words = set(words.words())

    # Step 1: Define Text Cleaning Function
    def clean_text(text):
        text = text.lower()
        text = re.sub(r"[@#]", " ", text)
        text = re.sub(r"[^\w\s]", " ", text)
        text = re.sub(r"\d+", " ", text)
        text = re.sub(r"\b\w{1,2}\b", " ", text)
        text = re.sub(r"\s+", " ", text).strip()
        return text

    # Load the CSV file into a Pandas DataFrame
    data_frame = pd.read_csv(input_csv, low_memory=False)

    # Specify the columns to process
    columns_to_process = ["company_name", "description", "title", "location", "skills_desc"]

    # Fill NaN values and clean text for the specified columns
    for col in columns_to_process:
        if col in data_frame.columns:
            data_frame[col] = data_frame[col].fillna("").apply(clean_text)
        else:
            print(f"Column '{col}' not found in DataFrame. Skipping...")

    # Initialize NLP Tools
    stop_words = set(stopwords.words("english"))
    lemmatizer = WordNetLemmatizer()

    def process_text(text):
        tokens = word_tokenize(text)
        lemmatized_tokens = [
            lemmatizer.lemmatize(token)
            for token in tokens
            if token not in stop_words and len(token) > 2 and token in english_words
        ]
        return lemmatized_tokens

    processed_tokens = []
    for col in columns_to_process:
        if col in data_frame.columns:
            data_frame[col] = data_frame[col].apply(lambda x: process_text(x))
            processed_tokens.extend(data_frame[col].explode().dropna())

    vocabulary_counter = Counter(processed_tokens)
    vocabulary = [word for word, _ in vocabulary_counter.most_common()]

    # Set preprocessing_dir as the current directory
    preprocessing_dir = Path(__file__).parent.resolve()  # Resolve ensures absolute path
    output_path = preprocessing_dir / output_csv

    # Ensure the directory exists
    preprocessing_dir.mkdir(parents=True, exist_ok=True)

    # Ensure the lexicon file exists or create it
    if not output_path.exists():
        pd.DataFrame(columns=["Word", "Index"]).to_csv(output_path, index=False)

    existing_lexicon = pd.read_csv(output_path)
    existing_words = set(existing_lexicon["Word"].dropna())
    next_index = existing_lexicon["Index"].max() + 1 if not existing_lexicon.empty else 0

    new_entries = [(word, idx) for idx, word in enumerate(vocabulary, start=next_index) if word not in existing_words]

    new_lexicon_df = pd.DataFrame(new_entries, columns=["Word", "Index"])

    if not new_lexicon_df.empty:
        new_lexicon_df.to_csv(output_path, mode="a", header=False, index=False)

    print(f"Unique words added to {output_csv}: {len(new_entries)}")
    print("Updated Vocabulary Size:", len(existing_words) + len(new_entries))

def process_text(text):
    # Dummy implementation of process_text
    return text.split()

# Example usage
# generate_lexicon("input.csv", "lexiconDynamic.csv")