import re
import requests
from bs4 import BeautifulSoup
import os
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv

load_dotenv()  # Loads variables from .env into the environment

# Access your keys like this:
CONFLUENCE_BASE_URL = os.getenv("CONFLUENCE_BASE_URL")
CONFLUENCE_API_TOKEN = os.getenv("CONFLUENCE_API_TOKEN")
CONFLUENCE_EMAIL = os.getenv("CONFLUENCE_EMAIL")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

auth = HTTPBasicAuth(CONFLUENCE_EMAIL, CONFLUENCE_API_TOKEN)

# Then use `auth` with your requests.get/post

def extract_page_id(url):
    match = re.search(r'/pages/(\d+)/', url)
    if not match:
        match = re.search(r'/content/(\d+)', url)
    return match.group(1) if match else None


import requests
from bs4 import BeautifulSoup
import os


CONFLUENCE_EMAIL = os.getenv("CONFLUENCE_EMAIL")
CONFLUENCE_API_TOKEN = os.getenv("CONFLUENCE_API_TOKEN")
CONFLUENCE_BASE_URL = os.getenv("CONFLUENCE_BASE_URL")
def extract_clean_text(soup):
    useful_text = []
    for tag in soup.find_all(["h1", "h2", "h3", "p", "li"]):
        text = tag.get_text(strip=True)
        if text:
            useful_text.append(text)
    return "\n".join(useful_text)

def fetch_confluence_content(page_id):
    url = f"{CONFLUENCE_BASE_URL}/wiki/rest/api/content/{page_id}?expand=body.storage"
    auth = HTTPBasicAuth(CONFLUENCE_EMAIL, CONFLUENCE_API_TOKEN)

    response = requests.get(url, auth=auth)
    print(f"Confluence API response status: {response.status_code}")
    if response.status_code != 200:
        print("Error fetching page content")
        return None, None, None, None, []

    data = response.json()
    title = data.get("title")
    html = data["body"]["storage"]["value"]
    soup = BeautifulSoup(html, "html.parser")
    extracted_text = extract_clean_text(soup)

    steps = []
    image_captions = {}

    # --- FIND IMAGES + CAPTIONS ---
    for figure in soup.find_all(["figure", "p"]):
        img_tag = figure.find("ac:image")
        if img_tag:
            # Try to find caption text
            caption = None

            # First check <figcaption> inside
            figcaption = figure.find("figcaption")
            if figcaption:
                caption = figcaption.get_text(strip=True)

            # Else check following sibling paragraph
            if not caption:
                next_p = figure.find_next_sibling("p")
                if next_p:
                    caption = next_p.get_text(strip=True)

            # Now check if caption looks like "Step 1", "Step 2" etc.
            if caption and "step" in caption.lower():
                step_number = ''.join(filter(str.isdigit, caption))  # extract number
                filename = None
                attachment = img_tag.find("ri:attachment")
                if attachment and "ri:filename" in attachment.attrs:
                    filename = attachment["ri:filename"]
                    if step_number:
                        image_captions[int(step_number)] = filename

    # --- FIND CONFIGURATION STEPS ---
    ol = soup.find("ol")
    if ol:
        li_elements = ol.find_all("li")
        for i, li in enumerate(li_elements):
            step_text = li.get_text(strip=True)
            step_number = i + 1
            filename = image_captions.get(step_number)

            steps.append({
                "text": step_text,
                "image": filename
            })

            print(f"Step {step_number}: {step_text}")
            print(f" → Image filename: {filename}")

    # Get all image filenames (for fallback overview image)
    all_image_filenames = []
    for img in soup.find_all("ac:image"):
        attachment = img.find("ri:attachment")
        if attachment and "ri:filename" in attachment.attrs:
            all_image_filenames.append(attachment["ri:filename"])

    overview_image = all_image_filenames[0] if all_image_filenames else None
    return title, extracted_text, steps, overview_image, all_image_filenames



def get_image_url(page_id, filename):
    return f"{CONFLUENCE_BASE_URL}/wiki/download/attachments/{page_id}/{filename}"

def test_confluence_api(page_id):
    url = f"{os.getenv('CONFLUENCE_BASE_URL')}/rest/api/content/{page_id}?expand=body.storage"
    headers = {
        "Authorization": f"Bearer {os.getenv('CONFLUENCE_API_TOKEN')}",
    }
    response = requests.get(url, headers=headers)
    print(f"Response status code: {response.status_code}")
    print(f"Response body: {response.text}")
    return response.status_code, response.text
def get_all_image_filenames(page_id):
    url = f"{CONFLUENCE_BASE_URL}/wiki/rest/api/content/{page_id}?expand=body.storage"
    headers = {
        "Authorization": f"Bearer {CONFLUENCE_API_TOKEN}",
        "Content-Type": "application/json"
    }

    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"Failed to fetch page content for images: {response.status_code}")
        return []

    html = response.json()["body"]["storage"]["value"]
    soup = BeautifulSoup(html, "html.parser")

    image_filenames = []
    for img in soup.find_all("ac:image"):
        attach = img.find("ri:attachment")
        if attach and attach.has_attr("ri:filename"):
            image_filenames.append(attach["ri:filename"])

    return image_filenames
def fetch_all_config_steps(page_id):
    url = f"{CONFLUENCE_BASE_URL}/wiki/rest/api/content/{page_id}?expand=body.storage"
    auth = HTTPBasicAuth(CONFLUENCE_EMAIL, CONFLUENCE_API_TOKEN)

    response = requests.get(url, auth=auth)
    if response.status_code != 200:
        print("Error fetching page content")
        return []

    data = response.json()
    html = data["body"]["storage"]["value"]
    soup = BeautifulSoup(html, "html.parser")

    steps = []
    ols = soup.find_all("ol")  # <-- Find ALL ordered lists, not just one
    if ols:
        for ol in ols:
            li_elements = ol.find_all("li")
            for li in li_elements:
                step_text = li.get_text(strip=True)
                if step_text:
                    steps.append({"text": step_text, "image": None})

    return steps

# Test the page with ID 66190
status_code, response_text = test_confluence_api(66190)