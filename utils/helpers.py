import base64
import requests
from requests.auth import HTTPBasicAuth
import os

CONFLUENCE_EMAIL = os.getenv("CONFLUENCE_EMAIL")
CONFLUENCE_API_TOKEN = os.getenv("CONFLUENCE_API_TOKEN")

def download_and_encode_image(img_url):
    try:
        auth = HTTPBasicAuth(CONFLUENCE_EMAIL, CONFLUENCE_API_TOKEN)
        headers = {"Accept": "application/json"}
        response = requests.get(img_url, headers=headers, auth=auth, timeout=10)

        print(f"🖼️ Image fetch status: {response.status_code} {img_url}")

        if response.status_code == 200:
            encoded = base64.b64encode(response.content).decode("utf-8")
            content_type = response.headers.get("Content-Type", "image/png")
            return f"data:{content_type};base64,{encoded}"
        else:
            print(f"⚠️ Failed to fetch image: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Exception fetching image: {e}")
        return None


import base64
import requests
from requests.auth import HTTPBasicAuth
import os

CONFLUENCE_EMAIL = os.getenv("CONFLUENCE_EMAIL")
CONFLUENCE_API_TOKEN = os.getenv("CONFLUENCE_API_TOKEN")

def download_image_as_base64(page_id, filename):
    confluence_base_url = os.getenv("CONFLUENCE_BASE_URL")
    img_url = f"{confluence_base_url}/wiki/download/attachments/{page_id}/{filename}"
    try:
        auth = HTTPBasicAuth(CONFLUENCE_EMAIL, CONFLUENCE_API_TOKEN)
        headers = {"Accept": "application/json"}
        response = requests.get(img_url, headers=headers, auth=auth, timeout=10)

        if response.status_code == 200:
            encoded = base64.b64encode(response.content).decode("utf-8")
            return f"data:image/png;base64,{encoded}"
        else:
            print(f"⚠️ Failed to fetch image: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Exception fetching image: {e}")
        return None