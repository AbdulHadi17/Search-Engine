from fastapi import FastAPI, UploadFile
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware  # Import CORSMiddleware
import pandas as pd
from pathlib import Path
import sys

# Add the parent directory of 'server' to the Python path
sys.path.append(str(Path(__file__).resolve().parent))

from Preprocessing.lexicon import generate_lexicon  # Corrected import

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
    try:
        # Save the uploaded file temporarily
        temp_file = Path("temp_postings.csv")
        with open(temp_file, "wb") as f:
            f.write(file.file.read())

        # Call the lexicon processing function
        output_file = Path("lexiconDynamic.csv")
        generate_lexicon(temp_file, output_file)

        return JSONResponse(
            content={"message": "Lexicon generated successfully", "output_file": str(output_file)},
            status_code=200,
        )
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)
