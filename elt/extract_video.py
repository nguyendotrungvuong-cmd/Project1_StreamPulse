from elt.youtube_client import get_youtube
import logging
from elt.logging_config import setup_logging
setup_logging()
logger = logging.getLogger(__name__)

def get_video_static(video_id):
    params = {"part": "snippet,statistics", "id": video_id}
    return get_youtube(params=params, endpoint="videos")
