import requests
import os
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv

load_dotenv()

CONFLUENCE_BASE_URL = os.getenv("CONFLUENCE_BASE_URL")
CONFLUENCE_API_TOKEN = os.getenv("CONFLUENCE_API_TOKEN")
CONFLUENCE_EMAIL = os.getenv("CONFLUENCE_EMAIL")

auth = HTTPBasicAuth(CONFLUENCE_EMAIL, CONFLUENCE_API_TOKEN)

def publish_release_note_to_confluence(title, html_content):
    url = f"{CONFLUENCE_BASE_URL}/wiki/rest/api/content"
    headers = {
        "Content-Type": "application/json"
    }
    data = {
        "type": "page",
        "title": title,
        "ancestors": [{"id": 524289}],  # Your parent page ID
        "space": {"key": "CGP"},
        "body": {
            "storage": {
                "value": html_content,
                "representation": "storage"
            }
        }
    }

    try:
        response = requests.post(url, auth=auth, headers=headers, json=data)

        if response.status_code in (200, 201):
            return True, "Successfully published to Confluence."
        elif response.status_code == 403:
            return False, "❌ 403 Forbidden: Check API token permissions or use Forge."
        else:
            print(f"Response: {response.status_code} - {response.text}")
            return False, f"Error publishing: {response.status_code} - {response.text}"

    except Exception as e:
        return False, f"❌ Exception: {str(e)}"
