from elt.youtube_client import get_youtube
import logging 
from elt.logging_config import setup_logging
setup_logging()
logger = logging.getLogger(__name__)


def get_all_videos_id(uploads_id):
    logging.info("Bắt đầu extract thông tin uploads")
    list_videos_id = []
    params = {
        "part": "snippet,contentDetails",
        "playlistId": uploads_id,
        "maxResults": 100,
    }
    data = get_youtube(params=params, endpoint="playlistItems")
    if not data: 
        raise ValueError(f"Lỗi: {ValueError}")
    all_pages = []
    while True:
        page = data.get("nextPageToken")
        if not page:
            break
        params["pageToken"] = page
        data = get_youtube(params=params, endpoint="playlistItems")
        all_pages.append(data)
    logging.info("Đã lấy thành công toàn bộ uploads")

    return all_pages
