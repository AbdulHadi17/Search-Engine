import json
import os
from collections import defaultdict


class BarrelManager:
    def __init__(self, output_dir: str):
        """
        Initialize the BarrelManager with the directory to store barrels.

        :param output_dir: Directory where barrels will be stored.
        """
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    @staticmethod
    def get_barrel(term: str) -> str:
        try:
            term_int = int(term)
            return str(term_int // 100)
        except ValueError:
            return None

    @staticmethod
    def get_bucket(term: str) -> str:
        try:
            term_int = int(term)
            return str(term_int % 10)
        except ValueError:
            return None

    def update_barrels_with_json(self, new_index_path: str) -> None:
        """
        Update barrels with terms and postings from a new inverted index JSON file.

        :param new_index_path: Path to the new inverted index JSON file.
        """
        if not os.path.exists(new_index_path):
            print(f"File not found: {new_index_path}")
            return

        with open(new_index_path, "r") as file:
            new_index = json.load(file)

        for term, new_postings in new_index.items():
            barrel_key = self.get_barrel(term)
            if not barrel_key:
                print(f"Invalid term '{term}': Unable to determine barrel.")
                continue

            bucket_key = self.get_bucket(term)
            if not bucket_key:
                print(f"Invalid term '{term}': Unable to determine bucket.")
                continue

            barrel_path = os.path.join(self.output_dir, f"{barrel_key}.json")

            # Load the existing barrel data or initialize a new one
            if os.path.exists(barrel_path):
                with open(barrel_path, "r") as file:
                    barrel_data = json.load(file)
            else:
                barrel_data = defaultdict(dict)

            # Access the bucket
            bucket = barrel_data.get(bucket_key, {})

            # If the term exists, update its postings
            if term in bucket:
                existing_postings = bucket[term]
                for new_posting in new_postings:
                    doc_id = new_posting["docID"]
                    found = False
                    for existing_posting in existing_postings:
                        if existing_posting["docID"] == doc_id:
                            existing_posting["frequency"] += new_posting["frequency"]
                            existing_posting["positions"].extend(new_posting["positions"])
                            existing_posting["positions"] = sorted(set(existing_posting["positions"]))
                            found = True
                            break
                    if not found:
                        existing_postings.append(new_posting)
            else:
                # If the term does not exist, add it
                bucket[term] = new_postings

            # Update the bucket in the barrel
            barrel_data[bucket_key] = bucket

            # Save the updated barrel data back to the file
            with open(barrel_path, "w") as file:
                json.dump(barrel_data, file, indent=4)

            print(f"Term '{term}' has been updated/added in barrel '{barrel_key}', bucket '{bucket_key}'.")

    def query_term(self, term: str) -> dict:
        barrel_key = self.get_barrel(term)
        if not barrel_key:
            return None

        bucket_key = self.get_bucket(term)
        if not bucket_key:
            return None

        barrel_path = os.path.join(self.output_dir, f"{barrel_key}.json")
        if os.path.exists(barrel_path):
            with open(barrel_path, "r") as file:
                barrel_data = json.load(file)
            return barrel_data.get(bucket_key, {}).get(term, None)
        return None
