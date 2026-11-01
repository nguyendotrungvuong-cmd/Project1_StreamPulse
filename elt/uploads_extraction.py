from elt.youtube_client import get_youtube
import logging

logger = logging.getLogger(__name__)


def get_all_videos_id(uploads_id):
    logger.info("Bắt đầu extract thông tin uploads")

    all_pages = []

    params = {
        "part": "snippet,contentDetails",
        "playlistId": uploads_id,
        "maxResults": 50,
    }

    while True:
        data = get_youtube(
            params=params,
            endpoint="playlistItems"
        )

        if not data:
            raise ValueError("Không lấy được dữ liệu uploads từ YouTube API")

        # Lưu cả trang đầu tiên
        all_pages.append(data)

        # Kiểm tra trang tiếp theo
        next_page_token = data.get("nextPageToken")

        if not next_page_token:
            break

        params["pageToken"] = next_page_token

    logger.info(
        "Đã lấy thành công %s trang uploads",
        len(all_pages)
    )
    total_items = sum(
    len(page.get("items", []))
    for page in all_pages
)

    logger.info("Tổng số video lấy được: %s", total_items)

    return all_pages