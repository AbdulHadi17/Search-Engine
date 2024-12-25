from fastapi import FastAPI, UploadFile
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware  # Import CORSMiddleware
from pathlib import Path
import sys
import pathlib
# Add the parent directory of 'server' to the Python path
sys.path.append(str(Path(__file__).resolve().parent))

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Frontend URL during development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/favicon.ico")
async def favicon():
    return JSONResponse(content={}, status_code=204)

@app.post("/api/process-csv/")
async def process_csv(file: UploadFile):
    temp_file = Path("temp_postings.csv")
    try:
        # Save the uploaded file temporarily
        with open(temp_file, "wb") as f:
            f.write(file.file.read())

        # Generate the lexicon
        output_path = (pathlib.Path().absolute() / "Preprocessing" /"lexicon.csv")
        from Preprocessing.LexiconGenerator import LexiconGenerator
        lex_gen = LexiconGenerator(output_path)
        lex_gen.generate(temp_file)

        # Generate the forward index
        forward_index_path = (pathlib.Path().absolute() / "Forward_Index" / "forward_index.json")
        new_forward_index_path = (pathlib.Path().absolute() / "Forward_Index" / "New_forward_index.json")
        from Forward_Index.ForwardIndexGenerator import ForwardIndexGenerator
        generator = ForwardIndexGenerator(temp_file, output_path, forward_index_path, new_forward_index_path)
        generator.generate_forward_index()

        # Generate the inverted index
        new_output_file_path = (pathlib.Path().absolute() / "inverted_index" / "New_Inverted.json")
        from inverted_index.InvertedIndexGenerator import InvertedIndexGenerator
        generator = InvertedIndexGenerator(new_forward_index_path, new_output_file_path)
        generator.generate()

        # Generate the barrels
        output_dir = (pathlib.Path().absolute() / "inverted_index" / "barrels")
        from inverted_index.BarrelManager import BarrelManager
        manager = BarrelManager(output_dir)
        manager.update_barrels_with_json(new_output_file_path)

        return JSONResponse(
            content={"message": "Successfully processed the document."},
            status_code=200,
        )
    except Exception as e:
        print(e)
        return JSONResponse(content={"error": str(e)}, status_code=500)
