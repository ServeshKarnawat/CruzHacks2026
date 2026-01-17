import csv
import random
import time
from pathlib import Path

DATA_PATH = Path(__file__).resolve().parent / "flex_sensor_data.csv"


def ensure_header(path: Path) -> None:
    if not path.exists() or path.stat().st_size == 0:
        with path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.writer(handle)
            writer.writerow(["Timestamp", "Raw_ADC", "Filtered_ADC", "Angle"])


def append_row(path: Path, raw_value: float, filtered: float, angle: float) -> None:
    timestamp = time.strftime("%H:%M:%S")
    with path.open("a", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow([timestamp, f"{raw_value:.2f}", f"{filtered:.2f}", f"{angle:.2f}"])


def main() -> None:
    ensure_header(DATA_PATH)
    raw = 500.0
    filtered = 500.0
    angle = 45.0

    while True:
        raw += random.uniform(-15, 15)
        raw = max(0, min(1023, raw))
        filtered = filtered * 0.8 + raw * 0.2
        angle = (filtered / 1023) * 90
        append_row(DATA_PATH, raw, filtered, angle)
        time.sleep(0.5)


if __name__ == "__main__":
    main()
