from elt.youtube_client import get_youtube
def channel_information(channel):
    params={
        "part":"snippet,contentDetails,statistics",
        "forHandle":channel,
    }
    return get_youtube(params=params,endpoint="channels")