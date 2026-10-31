from elt.youtube_client import get_youtube
import logging
logger = logging.getLogger(__name__)
def channel_information(channel):
    
        logger.info("Đang bắt đầu lấy thông tin channel")
        params={
            "part":"snippet,contentDetails,statistics",
            "forHandle":channel,
        }
        data = get_youtube(params=params,endpoint="channels")
        if not data or not data.get("items"):
            raise ValueError(f"Không tìm thấy tông tin {channel}") 
        logger.info(f"Đã lấy thông tin {channel} thành công")
        return data
        
        