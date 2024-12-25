from fastapi import FastAPI, UploadFile
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware  # Import CORSMiddleware
from pathlib import Path
import sys
import csv
import pathlib
from pydantic import BaseModel

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

# Define the request body schema
class QueryRequest(BaseModel):
    text: str


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

        data_file = (pathlib.Path().absolute() / "data" /"data.csv")  # Path to the existing data file

         # Append the content of temp_file to data.csv, excluding the header
        with open(temp_file, "r", newline="", encoding="utf-8") as temp_csv:
            temp_reader = csv.reader(temp_csv)
            temp_data = list(temp_reader)[1:]  # Skip the header row

        with open(data_file, "a", newline="", encoding="utf-8") as data_csv:
            data_writer = csv.writer(data_csv)
            data_writer.writerows(temp_data)

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
        print('a'+ e)
        return JSONResponse(content={"error": str(e)}, status_code=500)

@app.post("/api/get-query-result/")
async def get_query_result(request: QueryRequest):
    try:
        query = request.text.strip()

        # Perform search based on the query
        from search.singleSearch import SingleWordSearch
        from search.multiSearch import MultiWordSearch
        from Ranking.ranking import DocumentRankingUtility


        query_type = "single" if len(query.split()) == 1 else "multi"

        if query_type == "single":
            search_instance = SingleWordSearch(query)
            result = search_instance.search()
        else:
            search_instance = MultiWordSearch(query)
            result = search_instance.search()

        # Validate search result
        if not result or "filtered_results.json" not in result:
            return JSONResponse(content={"message": "No results found."}, status_code=404)

        # Perform ranking
        absolute_path = Path(__file__).resolve()
        filtered_result_path = absolute_path.parents[0] / 'Ranking' / 'filtered_results.json'
        metadata_file_path = absolute_path.parents[0] / 'data' / 'postings.csv'

        ranking_utility = DocumentRankingUtility(filtered_result_path, metadata_file_path)
        ranked_results = ranking_utility.rank()

        # Return ranked results
        return JSONResponse(content={"query": query, "ranked_results": ranked_results}, status_code=200)

    except Exception as e:
        print(e)
        return JSONResponse(content={"error": str(e)}, status_code=500)