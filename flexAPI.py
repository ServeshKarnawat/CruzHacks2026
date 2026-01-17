import csv
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse

BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR / "flex_sensor_data.csv"
INDEX_PATH = BASE_DIR / "index.html"
CSS_PATH = BASE_DIR / "main.css"

app = FastAPI()


def clean(value: object) -> str: #converts values to trimmed string
    return str(value).strip() if value is not None else "" 


@app.get("/", response_class=HTMLResponse) #Get index.html
def index() -> HTMLResponse:
    if not INDEX_PATH.exists():
        return HTMLResponse("Missing index.html", status_code=404)
    return HTMLResponse(INDEX_PATH.read_text(encoding="utf-8"))


@app.get("/main.css")
def main_css() -> FileResponse: #get main.css
    if not CSS_PATH.exists():
        return FileResponse("", status_code=404)
    return FileResponse(CSS_PATH)


@app.get("/latest")
def latest() -> JSONResponse: #get latest csv data
    if not DATA_PATH.exists():
        return JSONResponse({"error": f"Missing {DATA_PATH.name}"}, status_code=404) #throw if no datapath

    latest_row = None
    with DATA_PATH.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle) #reads the CSV and turns each row into a dictionary keyed by the header names from the first row.
        for row in reader: # Iterate through all rows so the last row is the latest.
            latest_row = row # Overwrite each loop; final value is the newest row.

    if latest_row is None: 
        return JSONResponse({"error": "No data in CSV"}, status_code=404)

    time_value = clean(
        latest_row.get("Timestamp") #get timestamp
    )
    flex_value = clean(latest_row.get("Filtered_ADC")) #get filtered_ADC
    return JSONResponse({"time": time_value, "flex": flex_value}) #sends JSON response with flex abd timestamp
