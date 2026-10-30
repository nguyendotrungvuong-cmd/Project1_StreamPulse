from elt.youtube_client import get_youtube
def get_video_static(video_id):
    params = {
        "part":"snippet,statistics",
        "id":video_id
    }
    return get_youtube(params=params,endpoint="videos")