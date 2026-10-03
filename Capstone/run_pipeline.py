"""
Bluestock Mutual Fund Capstone
Master Pipeline Execution Script

Runs the project's main notebooks in sequence:

1. Data ingestion
2. Data cleaning / transformation
3. EDA analysis
4. Performance analytics
"""

from pathlib import Path
import sys

try:
    import nbformat
    from nbclient import NotebookClient
except ImportError:
    print("Required packages are missing.")
    print("Install them with:")
    print("pip install nbformat nbclient")
    sys.exit(1)


PROJECT_ROOT = Path(__file__).resolve().parent
NOTEBOOK_DIR = PROJECT_ROOT / "notebooks"

NOTEBOOKS = [
    "01_data_ingestion.ipynb",
    "02_pipeline.ipynb",
    "03_eda_analysis.ipynb",
    "Performance_Analytics.ipynb",
]


def run_notebook(notebook_name: str) -> None:
    """Execute a Jupyter notebook and save its executed output."""

    notebook_path = NOTEBOOK_DIR / notebook_name

    if not notebook_path.exists():
        raise FileNotFoundError(
            f"Notebook not found: {notebook_path}"
        )

    print(f"\nRunning: {notebook_name}")

    with notebook_path.open("r", encoding="utf-8") as file:
        notebook = nbformat.read(file, as_version=4)

    client = NotebookClient(
        notebook,
        timeout=1800,
        kernel_name="python3",
        resources={
            "metadata": {
                "path": str(PROJECT_ROOT)
            }
        },
    )

    client.execute()

    with notebook_path.open("w", encoding="utf-8") as file:
        nbformat.write(notebook, file)

    print(f"Completed: {notebook_name}")


def main() -> None:
    """Run the complete Bluestock MF pipeline."""

    print("=" * 70)
    print("BLUESTOCK MF CAPSTONE - MASTER PIPELINE")
    print("=" * 70)

    for notebook in NOTEBOOKS:
        run_notebook(notebook)

    print("\n" + "=" * 70)
    print("PIPELINE COMPLETED SUCCESSFULLY")
    print("=" * 70)


if __name__ == "__main__":
    main()
