import csv
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse

BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR / "flex_sensor_data.csv"
INDEX_PATH = BASE_DIR / "index.html"
CSS_PATH = BASE_DIR / "main.css"

app = FastAPI()


def clean(value: object) -> str:
    return str(value).strip() if value is not None else ""


@app.get("/", response_class=HTMLResponse)
def index() -> HTMLResponse:
    if not INDEX_PATH.exists():
        return HTMLResponse("Missing index.html", status_code=404)
    return HTMLResponse(INDEX_PATH.read_text(encoding="utf-8"))


@app.get("/main.css")
def main_css() -> FileResponse:
    if not CSS_PATH.exists():
        return FileResponse("", status_code=404)
    return FileResponse(CSS_PATH)


@app.get("/latest")
def latest() -> JSONResponse:
    if not DATA_PATH.exists():
        return JSONResponse({"error": f"Missing {DATA_PATH.name}"}, status_code=404)

    latest_row = None
    with DATA_PATH.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            latest_row = row

    if latest_row is None:
        return JSONResponse({"error": "No data in CSV"}, status_code=404)

    time_value = clean(
        latest_row.get("time") or latest_row.get("Timestamp") or latest_row.get("timestamp")
    )
    flex_value = clean(
        latest_row.get("flex")
        or latest_row.get("Filtered_ADC")
        or latest_row.get("Angle")
        or latest_row.get("offset")
    )
    raw_value = clean(latest_row.get("Raw_ADC") or latest_row.get("steadiness"))
    return JSONResponse({"time": time_value, "flex": flex_value, "raw": raw_value})
