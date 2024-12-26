import pathlib
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent))

input_path = (pathlib.Path().absolute() /"server" / "data" / "postings.csv")
lexicon_path = (pathlib.Path().absolute() /"server" / "Preprocessing" /"lexicon.csv")
output_forward_index_path = (pathlib.Path().absolute() /"server" / "Forward_Index" /"forward_index.json")
new_forward_index_path = (pathlib.Path().absolute() /"server" / "Forward_Index" /"New_forward_index.json")
from ForwardIndexGenerator import ForwardIndexGenerator

generator = ForwardIndexGenerator(input_path, lexicon_path, output_forward_index_path, new_forward_index_path)
generator.generate_forward_index()
