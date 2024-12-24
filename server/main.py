from fastapi import FastAPI, UploadFile
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware  # Import CORSMiddleware
import pandas as pd
from pathlib import Path
import os
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
    temp_file = Path("temp_postings.csv")
    try:
        # Save the uploaded file temporarily
        with open(temp_file, "wb") as f:
            f.write(file.file.read())

        # Generate the lexicon
        generate_lexicon(temp_file)

        # Delete the temporary file after success
        if temp_file.exists():
            temp_file.unlink()  # Deletes the file

        return JSONResponse(
            content={"message": "Lexicon generated successfully"},
            status_code=200,
        )
    except Exception as e:
        # Ensure temp file is deleted in case of failure
        if temp_file.exists():
            temp_file.unlink()
        return JSONResponse(content={"error": str(e)}, status_code=500)
