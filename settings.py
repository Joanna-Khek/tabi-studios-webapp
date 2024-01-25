import os
from pathlib import Path

def get_root_dir(default_value: str = ".") -> Path:
    return Path(os.getenv("PIPELINE_ROOT_DIR", default_value))

ROOT_DIR = get_root_dir()
CSS_DIR = ROOT_DIR / "assets"
IMAGE_DIR = ROOT_DIR / "assets"