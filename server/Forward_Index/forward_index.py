import pandas as pd
import nltk
import json
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from nltk import pos_tag
import os
from pathlib import Path
from collections import defaultdict

# Download necessary NLTK resources
nltk.download('stopwords', quiet=True)
nltk.download('punkt', quiet=True)
nltk.download('wordnet', quiet=True)
nltk.download('averaged_perceptron_tagger', quiet=True)
nltk.download('omw-1.4', quiet=True)

# Load the dataset
absolute_path = Path(__file__).resolve()
csv_path = os.path.join(absolute_path.parents[1], 'data', 'dummy.csv')

# Load the lexicon from the CSV file
lexicon_path = os.path.join(absolute_path.parents[0], 'lexicon.csv')

# Check if the lexicon file exists
if not os.path.exists(lexicon_path):
    print(f"Error: The lexicon file was not found at {lexicon_path}. Creating a placeholder.")
    # Create a placeholder lexicon file with sample data
    sample_lexicon = pd.DataFrame({"Word": ["sample", "word"], "Index": [1, 2]})
    sample_lexicon.to_csv(lexicon_path, index=False)
    print(f"Placeholder lexicon file created at {lexicon_path}.")

# Load the lexicon file
lexicon_df = pd.read_csv(lexicon_path)

# Create a dictionary mapping words to their lexicon indices
vocabulary = dict(zip(lexicon_df['Word'], lexicon_df['Index']))

# Check if the dataset exists
if not os.path.exists(csv_path):
    raise FileNotFoundError(f"The dataset file was not found at {csv_path}.")

# Load the dataset
data = pd.read_csv(csv_path)

# Preprocessing function to tokenize, remove stopwords, and lemmatize
def preprocess_with_positions(text):
    stop_words = set(stopwords.words('english'))
    lemmatizer = WordNetLemmatizer()

    if pd.isnull(text):
        return []

    tokens = word_tokenize(text.lower())  # Tokenize and lowercase
    processed_tokens_with_positions = []
    for i, word in enumerate(tokens):
        if word.isalnum() and word not in stop_words and len(word) > 2:
            lemma = lemmatizer.lemmatize(word, get_wordnet_pos(pos_tag([word])[0][1]) or 'n')
            processed_tokens_with_positions.append((lemma, i))  # Append word and its position
    return processed_tokens_with_positions

# Map POS tags from Penn Treebank to WordNet format
def get_wordnet_pos(treebank_tag):
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

# Combine title and description for text processing
data['forward'] = data['title'] + " " + data['description']

# Apply preprocessing to text
data['processed_text_with_positions'] = data['forward'].apply(preprocess_with_positions)

# Build the forward index with frequency and positions
forward_index = {}
for index, row in data.iterrows():
    word_positions = defaultdict(list)
    for word, pos in row['processed_text_with_positions']:
        if word in vocabulary:  # Only consider words present in the lexicon
            word_positions[vocabulary[word]].append(pos)  # Use lexicon index instead of word

    # Format the word counts and positions in the desired way
    formatted_index = {}
    for word_index, positions in word_positions.items():
        formatted_index[word_index] = {
            "frequency": len(positions),
            "positions": positions
        }

    # Add formatted word counts and positions to the forward index
    forward_index[str(index)] = formatted_index

# Set the output path and ensure the directory exists
json_output_path = os.path.join(absolute_path.parents[0], 'forward_index.json')
output_dir = os.path.dirname(json_output_path)
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# Save the forward index to a JSON file
with open(json_output_path, 'w') as json_file:
    json.dump(forward_index, json_file, indent=4)

# Print confirmation message
print(f"Forward index with lexicon indices saved to {json_output_path}")
