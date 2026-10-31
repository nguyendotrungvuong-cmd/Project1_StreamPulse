import json
from pathlib import Path
from datetime import datetime, timezone
import logging

logger = logging.getLogger(__name__)


def save_raw_json(filename, data, run_id):
    logging.info(f"Bắt đầu lưu {filename} thành JSON")
    raw_dir = Path("data/raw")
    raw_dir.mkdir(parents=True, exist_ok=True)

    file_path = raw_dir / f"{filename}"
    if not file_path:
        raise ValueError(f"Không tìm thấy đường dẫn: {file_path}")
    collected_at = datetime.now(timezone.utc).isoformat()

    payload = {"run_id": run_id, "collected_at": collected_at, "data": data}

    with file_path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    logger.info(f"Đã lưu file {filename} thành công JSON ")
    return file_path
