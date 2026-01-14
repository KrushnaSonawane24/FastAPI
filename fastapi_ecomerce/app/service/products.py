import json
from pathlib import Path
from typing import List, Dict

BASE_DIR = Path(__file__).resolve().parent.parent
data_file = BASE_DIR / "data" / "dummy.json"

def load_products() -> List[Dict]:
    if not data_file.exists():
        return []

    try:
        with data_file.open("r", encoding="utf-8") as file:
            return json.load(file)
    except json.JSONDecodeError:
        return []

def get_all_products() -> List[Dict]:
    return load_products()
