import json
import os
from collections import defaultdict

# Path to the inverted index file (same directory as this script)
inverted_index_path = os.path.join(os.path.dirname(__file__), "inverted_index.json")

# Directory to store barrels (create it in the same directory as the script)
output_dir = os.path.join(os.path.dirname(__file__), "barrels")
os.makedirs(output_dir, exist_ok=True)

# Function to determine which barrel a term belongs to (based on term ID)
def get_barrel(term):
    try:
        term_int = int(term)  # Convert the term to an integer
        barrel_key = term_int // 100  # Divide by 1000 to get the barrel key
        return str(barrel_key)  # Return the barrel as a string (e.g., '20' for terms in the 20th range)
    except ValueError:
        return None  # Handle non-integer terms (if any)

# Function to determine which bucket within the barrel the term belongs to
def get_bucket(term):
    try:
        term_int = int(term)  # Convert the term to an integer
        bucket_key = term_int % 10  # Divide by 10 to determine the bucket key (0-9)
        return str(bucket_key)  # Return the bucket as a string (e.g., '3' for the 3rd bucket)
    except ValueError:
        return None  # Handle non-integer terms (if any)

# Load the inverted index
with open(inverted_index_path, "r") as file:
    inverted_index = json.load(file)

# Divide the inverted index into barrels and then buckets within each barrel
barrels = defaultdict(lambda: defaultdict(dict))  # Nested defaultdict for barrels and buckets

for term, postings in inverted_index.items():
    barrel_key = get_barrel(term)
    if barrel_key:
        bucket_key = get_bucket(term)
        if bucket_key:
            barrels[barrel_key][bucket_key][term] = postings

# Save each barrel and its buckets into separate JSON files
for barrel_key, barrel_data in barrels.items():
    barrel_path = os.path.join(output_dir, f"{barrel_key}.json")
    # We need to save barrels and buckets
    with open(barrel_path, "w") as file:
        json.dump(barrel_data, file, indent=4)

print(f"Barrels with buckets created and saved in '{output_dir}' directory.")

# Function to query a term from the barrels and buckets
def query_from_barrel_and_bucket(term):
    barrel_key = get_barrel(term)
    if not barrel_key:
        return None  # Term doesn't belong to any range

    bucket_key = get_bucket(term)
    if not bucket_key:
        return None  # Term doesn't belong to any bucket

    barrel_path = os.path.join(output_dir, f"{barrel_key}.json")
    if os.path.exists(barrel_path):
        with open(barrel_path, "r") as file:
            barrel_data = json.load(file)
        # Query the appropriate bucket and term
        return barrel_data.get(bucket_key, {}).get(term, None)
    return None
