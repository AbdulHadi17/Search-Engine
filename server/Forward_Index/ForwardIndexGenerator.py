import pandas as pd
import nltk
import json
import os
from pathlib import Path
from collections import defaultdict
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from nltk import pos_tag

# Download necessary NLTK resources
nltk.download('stopwords', quiet=True)
nltk.download('punkt', quiet=True)
nltk.download('wordnet', quiet=True)
nltk.download('averaged_perceptron_tagger', quiet=True)
nltk.download('omw-1.4', quiet=True)


class ForwardIndexGenerator:
    """
    A utility class to preprocess text, generate a forward index, and save it to JSON files.
    """

    def __init__(self, dataset_path, lexicon_path, output_json, new_json):
        """
        Initialize the generator with dataset, lexicon paths, and output file paths.

        Parameters:
            dataset_path (str): Path to the input CSV file.
            lexicon_path (str): Path to the lexicon CSV file.
            output_json (str): Path to save the combined forward index JSON.
            new_json (str): Path to save the newly generated forward index JSON.
        """
        self.dataset_path = dataset_path
        self.lexicon_path = lexicon_path
        self.output_json = output_json
        self.new_json = new_json
        self.vocabulary = self.load_lexicon()

    def load_lexicon(self):
        """
        Load the lexicon from a CSV file and create a word-to-index mapping.

        Returns:
            dict: A dictionary mapping words to their lexicon indices.
        """
        if not os.path.exists(self.lexicon_path):
            print(f"Error: The lexicon file was not found at {self.lexicon_path}. Creating a placeholder.")
            # Create a placeholder lexicon file with sample data
            sample_lexicon = pd.DataFrame({"Word": ["sample", "word"], "Index": [1, 2]})
            sample_lexicon.to_csv(self.lexicon_path, index=False)
            print(f"Placeholder lexicon file created at {self.lexicon_path}.")

        lexicon_df = pd.read_csv(self.lexicon_path)
        return dict(zip(lexicon_df['Word'], lexicon_df['Index']))

    def preprocess_with_positions(self, text):
        """
        Tokenize, lemmatize, and remove stopwords from the input text, preserving positions.

        Parameters:
            text (str): The input text to preprocess.

        Returns:
            list: A list of tuples containing lemmatized words and their positions.
        """
        stop_words = set(stopwords.words('english'))
        lemmatizer = WordNetLemmatizer()

        if pd.isnull(text):
            return []

        tokens = word_tokenize(text.lower())
        processed_tokens_with_positions = []
        for i, word in enumerate(tokens):
            if word.isalnum() and word not in stop_words and len(word) > 2:
                lemma = lemmatizer.lemmatize(word, self.get_wordnet_pos(pos_tag([word])[0][1]) or 'n')
                processed_tokens_with_positions.append((lemma, i))
        return processed_tokens_with_positions

    @staticmethod
    def get_wordnet_pos(treebank_tag):
        """
        Map Penn Treebank POS tags to WordNet POS tags.

        Parameters:
            treebank_tag (str): Penn Treebank POS tag.

        Returns:
            str: Corresponding WordNet POS tag.
        """
        if treebank_tag.startswith('J'):
            return 'a'
        elif treebank_tag.startswith('V'):
            return 'v'
        elif treebank_tag.startswith('N'):
            return 'n'
        elif treebank_tag.startswith('R'):
            return 'r'
        else:
            return None

    def load_existing_forward_index(self):
        """
        Load the existing forward index from the JSON file if it exists.

        Returns:
            dict: The existing forward index.
        """
        if os.path.exists(self.output_json):
            with open(self.output_json, 'r') as json_file:
                return json.load(json_file)
        return {}

    def generate_forward_index(self):
        """
        Generate a forward index for the dataset, append it to the existing index, and save to JSON files.
        """
        if not os.path.exists(self.dataset_path):
            raise FileNotFoundError(f"The dataset file was not found at {self.dataset_path}.")

        data = pd.read_csv(self.dataset_path)
        data.reset_index(drop=True, inplace=True)  # Ensure index is numeric
        data['forward'] = data['title'] + " " + data['description']
        data['processed_text_with_positions'] = data['forward'].apply(self.preprocess_with_positions)

        existing_forward_index = self.load_existing_forward_index()

        next_doc_id = max(map(int, existing_forward_index.keys()), default=-1) + 1
        forward_index = existing_forward_index
        new_index = {}

        for _, row in data.iterrows():  # Generate forward index for each document
            word_positions = defaultdict(list)
            for word, pos in row['processed_text_with_positions']:
                if word in self.vocabulary:
                    word_positions[self.vocabulary[word]].append(pos)

            formatted_index = {
                word_index: {
                    "frequency": len(positions),
                    "positions": positions
                }
                for word_index, positions in word_positions.items()
            }
            forward_index[str(next_doc_id)] = formatted_index
            new_index[str(next_doc_id)] = formatted_index  # Add to the new file
            next_doc_id += 1

        output_dir = os.path.dirname(self.output_json)
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        # Save the combined forward index
        with open(self.output_json, 'w') as json_file:
            json.dump(forward_index, json_file, indent=4)

        # Save the new index as a separate file
        with open(self.new_json, 'w') as new_json_file:
            json.dump(new_index, new_json_file, indent=4)

        print(f"Forward index saved to {self.output_json}")
        print(f"New index saved to {self.new_json}")
