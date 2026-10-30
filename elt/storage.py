import json
from pathlib import Path
from datetime import datetime, timezone


def save_raw_json(filename, data, run_id):

    raw_dir = Path("data/raw")
    raw_dir.mkdir(parents=True, exist_ok=True)

    file_path = raw_dir / f"{filename}.json"

    collected_at = datetime.now(timezone.utc).isoformat()

    payload = {
        "run_id": run_id,
        "collected_at": collected_at,
        "data": data
    }

    with file_path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    return file_path