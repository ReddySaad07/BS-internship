from pathlib import Path
import shutil


ROOT = Path(__file__).resolve().parents[1]

TARGETS = [
    ROOT / "db" / "nifty100.db",
    ROOT / "output",
    ROOT / "reports" / "tearsheets",
]


def clean():
    for target in TARGETS:

        if target.is_file():
            target.unlink()
            print(f"Removed: {target}")

        elif target.is_dir():
            for item in target.iterdir():
                if item.is_file():
                    item.unlink()

            print(f"Cleaned: {target}")


if __name__ == "__main__":
    clean()
