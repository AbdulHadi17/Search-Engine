import pandas as pd
import nltk
import json
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from collections import Counter
from nltk import pos_tag
import os
from pathlib import Path


# Download necessary NLTK resources
nltk.download('stopwords', quiet=True)
nltk.download('punkt', quiet=True)
nltk.download('wordnet', quiet=True)
nltk.download('averaged_perceptron_tagger', quiet=True)
nltk.download('omw-1.4', quiet=True);
# Load the dataset

absolute_path = Path(__file__).resolve(); 
csv_path = os.path.join(absolute_path.parents[1],'data','dummy.csv');

data = pd.read_csv(csv_path)

# Preprocessing function to tokenize, remove stopwords, and lemmatize
def preprocess(text):
    stop_words = set(stopwords.words('english'))
    lemmatizer = WordNetLemmatizer()

    if pd.isnull(text):
        return []

    tokens = word_tokenize(text.lower())  # Tokenize and lowercase
    processed_tokens = [
        lemmatizer.lemmatize(word, get_wordnet_pos(pos_tag([word])[0][1]) or 'n')
        for word in tokens
        if word.isalnum() and word not in stop_words and len(word) > 2
    ]
    return processed_tokens

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
data['text'] = data['title'] + " " + data['description']

# Apply preprocessing to text
data['processed_text'] = data['text'].apply(preprocess)

# Build the forward index using word frequencies
forward_index = {
    index: Counter(row['processed_text'])
    for index, row in data.iterrows()
}

# Set the output path and ensure the directory exists
json_output_path = os.path.join(absolute_path.parents[0],'forward_index.json');
output_dir = os.path.dirname(json_output_path)
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# Save the forward index to a JSON file
with open(json_output_path, 'w') as json_file:
    json.dump(forward_index, json_file, indent=4)

# Print confirmation message
print(f"Forward index saved to {json_output_path}")