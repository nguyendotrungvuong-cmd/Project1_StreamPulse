import logging
from pathlib import Path
import sys

def setup_logging():
    log_dir = Path("logs")
    log_dir.mkdir(parents=True, exist_ok=True)

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        handlers=[
            logging.FileHandler(log_dir / "pipeline.log", encoding="utf-8"),
            logging.StreamHandler(sys.stdout),
        ],
        force=True,
    )
