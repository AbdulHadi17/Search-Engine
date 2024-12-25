import pathlib
import sys
from pathlib import Path

# Add the 'inverted_index' directory to the Python path
sys.path.append(str(Path(__file__).resolve().parent))

# Define paths
inverted_index_path = (pathlib.Path().absolute() / "server" / "inverted_index" / "New_Inverted.json")
output_dir = (pathlib.Path().absolute() / "server" / "inverted_index" / "barrels")

from BarrelManager import BarrelManager
manager = BarrelManager(output_dir)

    # Update barrels with the new JSON
manager.update_barrels_with_json(inverted_index_path)

# Query a term
result = manager.query_term("54")
if result:
    print(f"Result for term '54': {result}")
else:
    print("Term '54' not found in the barrels.")