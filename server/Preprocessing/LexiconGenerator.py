import pandas as pd
import re
import nltk
from collections import Counter
from nltk.corpus import stopwords, words
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from pathlib import Path


class LexiconGenerator:
    """
    A utility class to generate and manage a lexicon from text data in CSV files.
    """

    def __init__(self, output_csv="dummy_lexicon.csv"):
        """
        Initializes the LexiconGenerator with the specified output file.

        Parameters:
            output_csv (str): Path to the output dummy lexicon file (default: 'dummy_lexicon.csv').
        """
        self.output_csv = output_csv
        nltk.download("punkt", quiet=True)
        nltk.download("stopwords", quiet=True)
        nltk.download("wordnet", quiet=True)
        nltk.download("words", quiet=True)
        self.english_words = set(words.words())

    def clean_text(self, text):
        """
        Cleans input text by removing special characters, numbers, and short words.

        Parameters:
            text (str): The text to clean.

        Returns:
            str: Cleaned text.
        """
        text = text.lower()
        text = re.sub(r"[@#]", " ", text)
        text = re.sub(r"[^\w\s]", " ", text)
        text = re.sub(r"\d+", " ", text)
        text = re.sub(r"\b\w{1,2}\b", " ", text)
        text = re.sub(r"\s+", " ", text).strip()
        return text

    def process_text(self, text):
        """
        Processes text by tokenizing, lemmatizing, and filtering stopwords.
        Relaxes the reliance on NLTK's `words.words`.

        Parameters:
            text (str): The text to process.

        Returns:
            list: Processed tokens.
        """
        stop_words = set(stopwords.words("english"))
        lemmatizer = WordNetLemmatizer()

        # Tokenize the text
        tokens = word_tokenize(text)

        # Filter tokens
        filtered_tokens = [
            lemmatizer.lemmatize(token.lower())  # Lemmatize and lowercase
            for token in tokens
            if token.lower() not in stop_words  # Exclude stopwords
            and len(token) > 2  # Minimum length 3
            and token.isalpha()  # Only alphabetic words
        ]

        return filtered_tokens

    def generate(self, input_csv):
        """
        Processes the input CSV file to generate or update a lexicon.

        Parameters:
            input_csv (str): Path to the input CSV file.
        """
        # Load CSV
        data_frame = pd.read_csv(input_csv, low_memory=False)

        # Specify columns to process
        columns_to_process = ["company_name", "description", "title", "location", "skills_desc"]

        # Fill NaN values and clean text
        for col in columns_to_process:
            if col in data_frame.columns:
                data_frame[col] = data_frame[col].fillna("").apply(self.clean_text)
            else:
                print(f"Column '{col}' not found in DataFrame. Skipping...")

        # Process text and build vocabulary
        processed_tokens = []
        for col in columns_to_process:
            if col in data_frame.columns:
                data_frame[col] = data_frame[col].apply(lambda x: self.process_text(x))
                processed_tokens.extend(data_frame[col].explode().dropna())

        vocabulary_counter = Counter(processed_tokens)
        vocabulary = [word for word, _ in vocabulary_counter.most_common()]

        # Set up output path
        preprocessing_dir = Path(__file__).parent.resolve()
        output_path = preprocessing_dir / self.output_csv
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

        print(f"Unique words added to {self.output_csv}: {len(new_entries)}")
        print("Updated Vocabulary Size:", len(existing_words) + len(new_entries))


# Example usage ==================================================================
# Create an instance of the LexiconGenerator and generate a lexicon from an input CSV
# if __name__ == "__main__":
#     lexicon_generator = LexiconGenerator("dummy_lexicon.csv")
#     lexicon_generator.generate("data/dummy.csv")
