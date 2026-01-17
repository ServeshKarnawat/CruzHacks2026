import csv
import random
import time
from pathlib import Path

DATA_PATH = Path(__file__).resolve().parent / "arm_stability_data.csv"

DIRECTIONS = ["STILL", "LEFT", "RIGHT", "FORWARD", "BACK", "DOWN"]


def ensure_header(path: Path) -> None:
    if not path.exists() or path.stat().st_size == 0:
        with path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.writer(handle)
            writer.writerow(
                ["Timestamp", "Flex_Value", "Accel_X", "Accel_Y", "Accel_Z", "Intensity", "Direction"]
            )


def append_row(path: Path, flex: float, ax: float, ay: float, az: float) -> None:
    intensity = (ax * ax + ay * ay + az * az) ** 0.5 / 10
    direction = "STILL" if intensity < 0.01 else random.choice(DIRECTIONS[1:])
    timestamp = time.strftime("%H:%M:%S")
    with path.open("a", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(
            [
                timestamp,
                f"{flex:.1f}",
                f"{ax:.3f}",
                f"{ay:.3f}",
                f"{az:.3f}",
                f"{intensity:.4f}",
                direction,
            ]
        )


def main() -> None:
    ensure_header(DATA_PATH)
    flex = 109.5
    ax, ay, az = -0.006, -0.003, 0.497

    while True:
        flex += random.uniform(-0.4, 0.4)
        flex = max(108.5, min(111.5, flex))

        ax += random.uniform(-0.02, 0.02)
        ay += random.uniform(-0.02, 0.02)
        az += random.uniform(-0.02, 0.02)

        ax = max(-0.2, min(0.45, ax))
        ay = max(-0.2, min(0.25, ay))
        az = max(-0.1, min(0.55, az))

        append_row(DATA_PATH, flex, ax, ay, az)
        time.sleep(0.01)


if __name__ == "__main__":
    main()
