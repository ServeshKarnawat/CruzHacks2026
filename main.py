import csv
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse

# FastAPI app that serves the results dashboard and the CSV-backed data feed.
app = FastAPI()

DATA_PATH = Path("data.csv")  # CSV columns: time, offset, steadiness
HTML_PATH = Path("results.html")  # Static HTML dashboard served at /



@app.get("/", response_class=HTMLResponse)
def index() -> HTMLResponse:
    # Serve the dashboard HTML so the frontend can fetch /data on the same origin.
    if not HTML_PATH.exists():
        return HTMLResponse("Missing results.html", status_code=404)
    return HTMLResponse(HTML_PATH.read_text(encoding="utf-8"))


@app.get("/data")
def data() -> JSONResponse:
    # Read the CSV on every request so the UI always shows the latest file contents.
    if not DATA_PATH.exists():
        return JSONResponse({"error": f"Missing {DATA_PATH.name}"}, status_code=404)

    with DATA_PATH.open(newline="", encoding="utf-8") as handle:
        # DictReader maps each CSV row into a dict using the header names.
        reader = csv.DictReader(handle)
        rows = [
            {
                # Keep strings here; the frontend parses numbers and formats labels.
                "time": row.get("time", "").strip(),
                "offset": row.get("offset", "").strip(),
                "steadiness": row.get("steadiness", "").strip(),
            }
            for row in reader
        ]
    return JSONResponse(rows)
