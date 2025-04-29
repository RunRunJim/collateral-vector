import os
import requests
from dotenv import load_dotenv

load_dotenv()

def generate_pdf_from_html(html_content):
    api_key = os.getenv("HTML2PDF_API_KEY")
    if not api_key:
        raise ValueError("⚠️ Missing HTML2PDF_API_KEY in environment variables.")

    print(f"🔎 HTML2PDF_API_KEY loaded on server: {api_key[:6]}...")

    url = f"https://api.html2pdf.app/v1/generate?apikey={api_key}"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }

    payload = {
        "html": html_content,
        "landscape": False,
        "printBackground": True
    }

    response = requests.post(url, headers=headers, json=payload)

    if response.status_code == 200:
        return response.content  # PDF file (bytes)
    else:
        print(f"⚠️ PDF generation failed:", response.text)
        return None


