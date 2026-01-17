import csv
import io
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse

BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR / "arm_stability_data.csv"
INDEX_PATH = BASE_DIR / "templates" / "index.html"
CSS_PATH = BASE_DIR / "main.css"
STATIC_CSS_PATH = BASE_DIR / "static" / "css" / "main.css"

app = FastAPI()

_csv_header = None
_last_pos = 0
_last_row = None


def clean(value: object) -> str: #converts values to trimmed string
    return str(value).strip() if value is not None else "" 


def get_latest_row() -> dict | None:
    global _csv_header, _last_pos, _last_row
    if not DATA_PATH.exists():
        return None

    file_size = DATA_PATH.stat().st_size
    if _last_pos > file_size:
        _csv_header = None
        _last_pos = 0
        _last_row = None

    with DATA_PATH.open(newline="", encoding="utf-8") as handle:
        if _last_pos == 0 or _csv_header is None:
            reader = csv.DictReader(handle)
            _csv_header = reader.fieldnames
            for row in reader:
                _last_row = row
            _last_pos = handle.tell()
            return _last_row

        handle.seek(_last_pos)
        new_data = handle.read()
        _last_pos = handle.tell()

    if not new_data.strip() or not _csv_header:
        return _last_row

    reader = csv.DictReader(io.StringIO(new_data), fieldnames=_csv_header)
    for row in reader:
        _last_row = row
    return _last_row


@app.get("/", response_class=HTMLResponse) #Get index.html
def index() -> HTMLResponse:
    if not INDEX_PATH.exists():
        return HTMLResponse("Missing index.html", status_code=404)
    return HTMLResponse(INDEX_PATH.read_text(encoding="utf-8"))



@app.get("/static/css/main.css")
def static_main_css() -> FileResponse: #get static/css/main.css
    if not STATIC_CSS_PATH.exists():
        return FileResponse("", status_code=404)
    return FileResponse(STATIC_CSS_PATH)


@app.get("/flex")
def flex() -> JSONResponse: #get latest csv data
    if not DATA_PATH.exists():
        return JSONResponse({"error": f"Missing {DATA_PATH.name}"}, status_code=404) #throw if no datapath

    latest_row = get_latest_row()
    if latest_row is None: 
        return JSONResponse({"error": "No data in CSV"}, status_code=404)


    flex_value = clean(latest_row.get("Flex_Value")) #get flex value
    return JSONResponse({ "flex": flex_value}) #sends JSON response with flex value



@app.get("/stability")
def stability() -> JSONResponse: #get latest accel data
    if not DATA_PATH.exists():
        return JSONResponse({"error": f"Missing {DATA_PATH.name}"}, status_code=404) 

    latest_row = get_latest_row()
    if latest_row is None:
        return JSONResponse({"error": "No data in CSV"}, status_code=404)

    try:
        intensity = float(clean(latest_row.get("Intensity")))
    except (TypeError, ValueError):
        return JSONResponse({"error": "Invalid intensity data"}, status_code=400)

    return JSONResponse({"intensity": intensity})
