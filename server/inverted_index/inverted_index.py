import pathlib
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent))

output_file_path = (pathlib.Path().absolute() /"server" / "inverted_index" /"inverted_index.json")
forward_index_path = (pathlib.Path().absolute() /"server" / "Forward_Index" /"forward_index.json")

from InvertedIndexGenerator import InvertedIndexGenerator

generator = InvertedIndexGenerator(forward_index_path, output_file_path)
generator.generate()
