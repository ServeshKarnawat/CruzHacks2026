import csv
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse

# FastAPI app that serves the results dashboard and the CSV-backed data feed.
app = FastAPI()

BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR / "flex_sensor_data.csv"  # CSV columns: time, flex, steadiness (if present)
HTML_PATH = BASE_DIR / "results.html"  # Static HTML dashboard served at /
SESSION_PATH = BASE_DIR / "session.html"  # Flex bar view



@app.get("/", response_class=HTMLResponse)
def index() -> HTMLResponse:
    # Serve the dashboard HTML so the frontend can fetch /data on the same origin.
    if not HTML_PATH.exists():
        return HTMLResponse("Missing results.html", status_code=404)
    return HTMLResponse(HTML_PATH.read_text(encoding="utf-8"))


@app.get("/session", response_class=HTMLResponse)
def session() -> HTMLResponse:
    # Serve the flex bar view.
    if not SESSION_PATH.exists():
        return HTMLResponse("Missing session.html", status_code=404)
    return HTMLResponse(SESSION_PATH.read_text(encoding="utf-8"))


@app.get("/data")
def data() -> JSONResponse:
    # Read the CSV on every request so the UI always shows the latest file contents.
    if not DATA_PATH.exists():
        return JSONResponse({"error": f"Missing {DATA_PATH.name}"}, status_code=404)

    def clean(value: object) -> str:
        return str(value).strip() if value is not None else ""

    with DATA_PATH.open(newline="", encoding="utf-8") as handle:
        # DictReader maps each CSV row into a dict using the header names.
        reader = csv.DictReader(handle)
        rows = []
        for index, row in enumerate(reader, start=1):
            # Keep strings here; the frontend parses numbers and formats labels.
            mapped = {
                "time": clean(row.get("time") or row.get("Timestamp") or row.get("timestamp")),
                "offset": clean(
                    row.get("flex")
                    or row.get("Filtered_ADC")
                    or row.get("Angle")
                    or row.get("offset")
                ),
                "steadiness": clean(row.get("steadiness") or row.get("Raw_ADC")),
            }
            if index % 380 == 0:
                rows.append(mapped)
            last_row = mapped

        if rows and rows[-1] != last_row:
            rows.append(last_row)
        elif not rows and "last_row" in locals():
            rows.append(last_row)
    return JSONResponse(rows)


@app.get("/flex")
def flex() -> JSONResponse:
    # Return the latest flex value for the realtime slider.
    if not DATA_PATH.exists():
        return JSONResponse({"error": f"Missing {DATA_PATH.name}"}, status_code=404)

    def clean(value: object) -> str:
        return str(value).strip() if value is not None else ""

    latest_row = None
    with DATA_PATH.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            latest_row = row

    if latest_row is None:
        return JSONResponse({"error": "No data in CSV"}, status_code=404)

    flex_value = clean(
        latest_row.get("flex")
        or latest_row.get("Filtered_ADC")
        or latest_row.get("Angle")
        or latest_row.get("offset")
    )
    time_value = clean(
        latest_row.get("time") or latest_row.get("Timestamp") or latest_row.get("timestamp")
    )
    return JSONResponse({"time": time_value, "flex": flex_value})
