"""Load local settings from config.yaml (not under version control)."""
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent
CONFIG_FILE = ROOT / "config.yaml"


def load_config() -> dict:
    if not CONFIG_FILE.exists():
        raise FileNotFoundError(
            "config.yaml not found. Copy config.example.yaml to config.yaml "
            "and set the data paths for this machine."
        )
    with CONFIG_FILE.open(encoding="utf-8") as f:
        cfg = yaml.safe_load(f)
    for key, value in cfg["data"].items():
        cfg["data"][key] = Path(value)
    cfg["output"] = Path(cfg["output"])
    cfg["output"].mkdir(parents=True, exist_ok=True)
    return cfg


def check_paths() -> None:
    """Print whether each configured data folder exists."""
    cfg = load_config()
    for key, path in cfg["data"].items():
        status = "ok" if path.exists() else "MISSING"
        print(f"{key:14s} {status:8s} {path}")


if __name__ == "__main__":
    check_paths()
