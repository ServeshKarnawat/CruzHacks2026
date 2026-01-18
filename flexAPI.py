import csv
import io
import threading 
import serial
import time
import os
import signal
import graph
import pandas as pd
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates


BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR / "arm_stability_data.csv"
INDEX_PATH = BASE_DIR / "templates" / "index.html"
CSS_PATH = BASE_DIR / "main.css"
STATIC_CSS_PATH = BASE_DIR / "static" / "css" / "main.css"
STATIC_RESULTS_PATH = BASE_DIR / "static" / "css" / "results.css"
RESULTS_PATH = BASE_DIR/ "templates" / "results.html"


SERIAL_PORT = "/dev/cu.usbmodem1103" 
BAUD_RATE = 115200
logging_active = True # This flag controls the loop

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

def start_logging():
    global logging_active
    try:
        # Open serial port
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
        
        # Open CSV and write header
        with open(DATA_PATH, mode='w', newline='') as f:
            writer = csv.writer(f)
            header = ["Timestamp", "Flex_Value", "Accel_X", "Accel_Y", "Accel_Z", "Stability", "Intensity", "Direction", "Rep_Count"]
            writer.writerow(header)

            while logging_active:
                if ser.in_waiting > 0:
                    line = ser.readline().decode('utf-8', errors='ignore').strip()
                    if line:
                        data_points = line.split(',')
                        if len(data_points) == 8:
                            curr_time = time.strftime("%H:%M:%S")
                            writer.writerow([curr_time] + data_points)
                            f.flush() # Ensure data is written to disk immediately
        ser.close()
    except Exception as e:
        print(f"Logging Error: {e}")

# --- NEW: START LOGGER ON BOOT ---
# This starts the function above in a separate 'thread' so the website can still run
threading.Thread(target=start_logging, daemon=True).start()

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

@app.get("/results", response_class=HTMLResponse)
async def get_results(request: Request):
    if not DATA_PATH.exists():
        return HTMLResponse("CSV file not found.", status_code=404)

    try:
        # ---- Stability average ----
        stability_sum = 0
        stability_count = 0
        flex_peaks = []

        # rep total
        df = pd.read_csv('arm_stability_data.csv')
        total_reps = df['Rep_Count'].max()

        for chunk in pd.read_csv(
            DATA_PATH,
            usecols=["Flex_Value", "Stability"],
            chunksize=100_000
        ):
            # Stability mean
            stability_sum += chunk["Stability"].sum()
            stability_count += chunk["Stability"].count()

            # Flex peaks
            flex = chunk["Flex_Value"].fillna(0).values
            for i in range(1, len(flex) - 1):
                if flex[i] > flex[i - 1] and flex[i] > flex[i + 1]:
                    flex_peaks.append(flex[i])

        stability_avg = stability_sum / stability_count if stability_count else 0
        flex_peaks = sorted(flex_peaks, reverse=True)[:200]

        return templates.TemplateResponse("results.html", {
            "request": request,
            "flex_data": flex_peaks,
            "stability_data": stability_avg,
            "reps": total_reps
        })

    except Exception as e:
        print(f"Error processing results: {e}")
        return HTMLResponse(f"Internal Server Error: {e}", status_code=500)


@app.get("/rom.html", response_class=HTMLResponse)
def get_rom():
    # Assuming these are in your templates folder
    rom_path = BASE_DIR / "templates" / "rom.html"
    if not rom_path.exists():
        return HTMLResponse("Missing rom.html", status_code=404)
    return HTMLResponse(rom_path.read_text(encoding="utf-8"))

@app.get("/steady.html", response_class=HTMLResponse)
def get_steady():
    # Assuming these are in your templates folder
    steady_path = BASE_DIR / "templates" / "steady.html"
    if not steady_path.exists():
        return HTMLResponse("Missing steady.html", status_code=404)
    return HTMLResponse(steady_path.read_text(encoding="utf-8"))

@app.post("/stop-collection")
def stop_collection():
    global logging_active
    logging_active = False
    df =pd.read_csv("arm_stability_data.csv")
    graph.plot_rom(df)
    graph.plot_steady(df)
    # This sends a SIGINT (Control+C signal) to the process itself
    print("Logging stoppped server running")
    return {"status": "success"}

@app.get("/static/css/main.css")
def static_main_css() -> FileResponse: #get static/css/main.css
    if not STATIC_CSS_PATH.exists():
        return FileResponse("", status_code=404)
    return FileResponse(STATIC_CSS_PATH)

@app.get("/results/css/results.css")
def read_results() -> FileResponse:
    if not STATIC_RESULTS_PATH.exists():
        return FileResponse("Missing results.html", status_code=404)
    return FileResponse(STATIC_RESULTS_PATH)


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