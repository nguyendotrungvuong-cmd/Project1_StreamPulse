from dotenv import load_dotenv
import os
import requests
load_dotenv()



def get_youtube(params,endpoint):
    api = os.getenv("api")
    base_url = os.getenv("url")
    query = {
        **params,
        "key":api
    }
    url = f"{base_url}/{endpoint}"
    respones = requests.get(url,params=query,timeout=20)
    respones.raise_for_status()
    data = respones.json()
    return data