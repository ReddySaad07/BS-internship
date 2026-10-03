from pathlib import Path
import yaml


ROOT = Path(__file__).resolve().parents[2]


def load_config():
    """Load the screener YAML configuration."""
    path = ROOT / "config" / "screener_config.yaml"

    with open(path, "r", encoding="utf-8") as file:
        return yaml.safe_load(file)


def project_root():
    return ROOT
