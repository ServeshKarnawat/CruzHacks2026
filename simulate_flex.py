import csv
import random
import time
from pathlib import Path

DATA_PATH = Path(__file__).resolve().parent / "flex_sensor_data.csv"


def append_row(path: Path, raw_value: float, filtered: float) -> None:
    timestamp = time.strftime("%H:%M:%S")
    with path.open("a", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow([timestamp, f"{raw_value:.0f}", f"{filtered:.2f}"])


def main() -> None:
    raw = 125.0
    filtered = 125.0

    while True:
        if random.random() < 0.2:
            raw += random.uniform(-30, 30)
        else:
            raw += random.uniform(-8, 8)
        raw = max(80, min(180, raw))
        filtered = filtered * 0.8 + raw * 0.2
        append_row(DATA_PATH, raw, filtered)
        time.sleep(0.5)


if __name__ == "__main__":
    main()
