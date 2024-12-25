import pathlib
import sys
from pathlib import Path

# Add the 'Preprocessing' directory to the Python path
sys.path.append(str(Path(__file__).resolve().parent))

input_path = (pathlib.Path().absolute()/"server" / "data" / "data.csv")
output_path = (pathlib.Path().absolute() /"server" / "Preprocessing" /"lexicon.csv")
from LexiconGenerator import LexiconGenerator

# Initialize the generator
lex_gen = LexiconGenerator(output_path)

# Generate or update the lexicon from a CSV file
lex_gen.generate(input_path)
