import json
from collections import defaultdict
import os
from pathlib import Path


#Current Location of this file
absolute_path = Path(__file__).resolve();

#Going to base Directory to make dynamic paths
path_forward_index = os.path.join(absolute_path.parents[1], 'Forward_Index', 'forward_index.json');

# Similarly, Location to save the json output
path_output_file = os.path.join(absolute_path.parents[0],'inverted_index.json') ;


# This makes sure that the forward indexed file already exists.
try:
    with open(path_forward_index, 'r') as file:
        forward_index = json.load(file) 
except FileNotFoundError:
    print(f"Error: The forward index file at {path_forward_index} was not found.");
    #remove the below file as soon as the code merges
    forward_index ={
        #dummy data 
    0: {"java": {"frequency": 3, "positions": [0, 2, 5]},
        "engineer": {"frequency": 2, "positions": [1, 4]}},
    1: {"analytics": {"frequency": 2, "positions": [0, 3]},
        "java": {"frequency": 1, "positions": [2]},
        "visualize": {"frequency": 1, "positions": [5]}},
    2: {"engineer": {"frequency": 3, "positions": [0, 3, 6]},
        "java": {"frequency": 4, "positions": [1, 2, 5, 7]},
        "analytics": {"frequency": 2, "positions": [0, 4]}}
}



# initializing the dictionary
inverted_index = defaultdict(list);



#creating inverted index
for docID, words in forward_index.items():
    for word, metadata in words.items():
        inverted_index[word].append({
            "docID": docID,
            "frequency": metadata["frequency"],
            "positions": metadata["positions"]
        })

#sorting for efficiency
for word in inverted_index:
    inverted_index[word] = sorted(inverted_index[word], key=lambda x: x['frequency'], reverse=True);

#replacing if file exists
output_directory = os.path.dirname(path_output_file)
if not os.path.exists(output_directory):
    os.makedirs(output_directory)

with open(path_output_file, 'w') as json_file:
    json.dump(inverted_index, json_file, indent=4);

print(f"Inverted index json file has been saved to {path_output_file}");
