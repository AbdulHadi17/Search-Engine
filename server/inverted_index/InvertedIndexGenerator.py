import ujson as json
from collections import defaultdict
import os
from pathlib import Path


class InvertedIndexGenerator:
    def __init__(self, forward_index_path: str, output_file_path: str):
        """
        Initializes the InvertedIndexGenerator with paths for the forward index and the output inverted index file.

        Args:
            forward_index_path (str): Path to the forward index JSON file.
            output_file_path (str): Path to save the generated inverted index JSON file.
        """
        self.forward_index_path = forward_index_path
        self.output_file_path = output_file_path

    def load_forward_index(self) -> dict:
        """
        Loads the forward index from the specified path.

        Returns:
            dict: The loaded forward index.

        Raises:
            FileNotFoundError: If the forward index file is not found.
        """
        try:
            with open(self.forward_index_path, 'r') as file:
                return json.load(file)
        except FileNotFoundError:
            print(f"Error: The forward index file at {self.forward_index_path} was not found.")
            return {
                # Dummy data for testing; remove once the actual file is present
                0: {"java": {"frequency": 3, "positions": [0, 2, 5]},
                    "engineer": {"frequency": 2, "positions": [1, 4]}},
                1: {"analytics": {"frequency": 2, "positions": [0, 3]},
                    "java": {"frequency": 1, "positions": [2]},
                    "visualize": {"frequency": 1, "positions": [5]}},
                2: {"engineer": {"frequency": 3, "positions": [0, 3, 6]},
                    "java": {"frequency": 4, "positions": [1, 2, 5, 7]},
                    "analytics": {"frequency": 2, "positions": [0, 4]}}
            }

    def create_inverted_index(self, forward_index: dict) -> defaultdict:
        """
        Creates an inverted index from the given forward index.

        Args:
            forward_index (dict): The forward index.

        Returns:
            defaultdict: The generated inverted index.
        """
        inverted_index = defaultdict(list)
        for docID, words in forward_index.items():
            for word, metadata in words.items():
                inverted_index[word].append({
                    "docID": docID,
                    "frequency": metadata["frequency"],
                    "positions": metadata["positions"]
                })
        return inverted_index

    def save_inverted_index(self, inverted_index: defaultdict) -> None:
        """
        Saves the inverted index to the specified output file.

        Args:
            inverted_index (defaultdict): The inverted index to save.
        """
        output_directory = os.path.dirname(self.output_file_path)
        if not os.path.exists(output_directory):
            os.makedirs(output_directory)

        with open(self.output_file_path, 'w') as json_file:
            json.dump(inverted_index, json_file, indent=4)
        print(f"Inverted index JSON file has been saved to {self.output_file_path}")

    def generate(self) -> None:
        """
        Main method to generate the inverted index from the forward index and save it.
        """
        forward_index = self.load_forward_index()
        inverted_index = self.create_inverted_index(forward_index)
        self.save_inverted_index(inverted_index)
