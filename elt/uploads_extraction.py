from elt.youtube_client import get_youtube
def get_all_videos_id(uploads_id):
    list_videos_id = []
    params = {
        "part": "snippet,contentDetails",
        "playlistId": uploads_id,
        "maxResults": 100
    }
    data = get_youtube(params=params,endpoint="playlistItems")
    all_pages = []
    while True:
        page = data.get("nextPageToken")
        if not page:
            break
        params["pageToken"]= page
        data = get_youtube(params=params,endpoint="playlistItems")
        all_pages.append(data)
    return all_pages