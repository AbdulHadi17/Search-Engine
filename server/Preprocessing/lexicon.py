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
