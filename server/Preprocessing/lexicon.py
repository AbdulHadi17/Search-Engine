# Import necessary libraries
import pandas as pd
import re
import nltk
from collections import Counter
from nltk.corpus import stopwords, words
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from pathlib import Path

def generate_lexicon(input_csv, output_csv):
    """
    Generates a lexicon from the input CSV file and saves it to the specified output file.
    
    Parameters:
        input_csv (str): Path to the input CSV file.
        output_csv (str): Path to save the output lexicon file.
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
        """
        Cleans the input text by:
        - Converting to lowercase.
        - Removing special characters, digits, extra whitespace, and unwanted patterns.
        """
        text = text.lower()
        text = re.sub(r"[@#]", " ", text)  # Replace @ and # with a space
        text = re.sub(r"[^\w\s]", " ", text)  # Remove non-alphanumeric characters
        text = re.sub(r"\d+", " ", text)  # Remove digits
        text = re.sub(r"\b\w{1,2}\b", " ", text)  # Remove very short words (1-2 characters)
        text = re.sub(r"\s+", " ", text).strip()  # Remove extra whitespace
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

    # Step 4: Tokenize, Remove Stopwords, and Lemmatize
    def process_text(text):
        """
        Processes the text by:
        - Tokenizing.
        - Removing stopwords.
        - Lemmatizing tokens.
        - Filtering non-English words and garbage tokens.
        """
        tokens = word_tokenize(text)
        lemmatized_tokens = [
            lemmatizer.lemmatize(token)
            for token in tokens
            if token not in stop_words and len(token) > 2 and token in english_words
        ]
        return lemmatized_tokens

    # Apply processing to all specified columns and aggregate tokens
    processed_tokens = []
    for col in columns_to_process:
        if col in data_frame.columns:
            data_frame[col] = data_frame[col].apply(lambda x: process_text(x))
            processed_tokens.extend(data_frame[col].explode().dropna())

    # Step 5: Build Vocabulary
    vocabulary_counter = Counter(processed_tokens)
    vocabulary = {word: idx for idx, (word, _) in enumerate(vocabulary_counter.most_common())}

    # Step 6: Save Vocabulary to a CSV File
    vocabulary_df = pd.DataFrame(vocabulary.items(), columns=["Word", "Index"])
    vocabulary_df.to_csv(output_csv, index=False)

    # Output results
    print(f"Lexicon saved successfully to {output_csv}")
    print("Vocabulary Size:", len(vocabulary))
