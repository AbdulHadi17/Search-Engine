# Import necessary libraries
import pandas as pd
import re
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer

# Ensure necessary NLTK data is downloaded
nltk.download("punkt", quiet=True)
nltk.download("stopwords", quiet=True)
nltk.download("wordnet", quiet=True)
nltk.download("omw-1.4", quiet=True)

# Step 1: Load Data
# Load the CSV file into a Pandas DataFrame
# Ensure the file path is correct
data_frame = pd.read_csv("server/Preprocessing/dummy.csv")

# Specify the columns to process
columns_to_process = ["company_name", "description", "title", "location", "skills_desc"]

# Fill NaN values for specified columns
for col in columns_to_process:
    if col in data_frame.columns:
        data_frame[col] = data_frame[col].fillna("").astype(str)
    else:
        print(f"Column '{col}' not found in DataFrame. Skipping...")


# Step 2: Initialize NLP Tools
# Load English stopwords
stop_words = set(stopwords.words("english"))
# Initialize lemmatizer
lemmatizer = WordNetLemmatizer()

# Step 3: Define Text Cleaning Function
def clean_text(text):
    """
    Cleans the input text by:
    - Converting to lowercase.
    - Removing special characters, digits, and extra whitespace.
    """
    text = text.lower()
    text = re.sub(r"[@#]", " ", text)  # Replace @ and # with a space
    text = re.sub(r"[^\w\s]", " ", text)  # Remove non-alphanumeric characters
    text = re.sub(r"\d+", "", text)  # Remove digits
    text = re.sub(r"\s+", " ", text).strip()  # Remove extra whitespace
    return text

# Apply text cleaning to the specified columns
for col in columns_to_process:
    if col in data_frame.columns:
        data_frame[col] = data_frame[col].apply(clean_text)

# Step 4: Define Text Processing Function
def process_text(text):
    """
    Processes the text by:
    - Tokenizing into words.
    - Removing stopwords.
    - Lemmatizing tokens.
    """
    tokens = word_tokenize(text)  # Tokenize text
    tokens = [token for token in tokens if token not in stop_words]  # Remove stopwords
    lemmatized_tokens = [lemmatizer.lemmatize(token) for token in tokens]  # Lemmatize tokens
    return lemmatized_tokens

# Apply text processing to the specified columns
processed_texts = []  # List to store processed tokens from all columns
for col in columns_to_process:
    if col in data_frame.columns:
        column_tokens = data_frame[col].apply(process_text)
        processed_texts.extend(column_tokens)  # Append processed tokens to the list
