from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.lib import colors
from datetime import date
import io
import requests
from utils.ai_helpers import generate_summary_and_steps
from utils.confluence import get_image_url
from requests.auth import HTTPBasicAuth
import os

CONFLUENCE_EMAIL = os.getenv("CONFLUENCE_EMAIL")
CONFLUENCE_API_TOKEN = os.getenv("CONFLUENCE_API_TOKEN")

auth = HTTPBasicAuth(CONFLUENCE_EMAIL, CONFLUENCE_API_TOKEN)

def download_image(img_url):
    try:
        headers = {"Accept": "application/json"}
        response = requests.get(img_url, headers=headers, auth=auth, timeout=10)
        if response.status_code == 200:
            return io.BytesIO(response.content)
        else:
            print(f"⚠️ Failed to fetch image: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Exception fetching image: {e}")
        return None

def build_pdf(feature_title, content, page_id, overview_image=None, all_image_filenames=None):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    margin = 50
    y = height - margin

    today = date.today().strftime('%B %d, %Y')

    # Title Section
    c.setFont("Helvetica-Bold", 20)
    c.setFillColor(colors.HexColor("#0085CA"))
    c.drawCentredString(width / 2, y, "Awesome Helpful Feature Guide")
    y -= 30

    c.setFont("Helvetica-Bold", 16)
    c.drawCentredString(width / 2, y, feature_title)
    y -= 20

    c.setFont("Helvetica", 12)
    c.setFillColor(colors.black)
    c.drawCentredString(width / 2, y, today)
    y -= 40

    # Overview Section
    ai_response = generate_summary_and_steps(content)
    refined_summary = content  # fallback
    config_steps = []

    if ai_response and "Configuration Steps:" in ai_response:
        try:
            summary_part, steps_part = ai_response.split("Configuration Steps:")
            refined_summary = summary_part.replace("Feature Summary:", "").strip()
            config_steps = [line.strip() for line in steps_part.strip().split("\n") if line.strip()]
        except Exception as e:
            print("⚠️ Failed to parse AI output:", e)

    c.setFont("Helvetica-Bold", 14)
    c.drawString(margin, y, "Overview:")
    y -= 20

    c.setFont("Helvetica", 12)
    for line in refined_summary.splitlines():
        c.drawString(margin, y, line)
        y -= 16
        if y < 100:
            c.showPage()
            y = height - margin

    if overview_image:
        img_url = get_image_url(page_id, overview_image)
        img_stream = download_image(img_url)
        if img_stream:
            try:
                c.drawImage(ImageReader(img_stream), margin, y - 200, width=400, preserveAspectRatio=True, mask='auto')
                y -= 220
            except Exception as e:
                print(f"⚠️ Failed to draw overview image: {e}")

    y -= 20

    # Configuration Steps Section
    c.setFont("Helvetica-Bold", 14)
    c.drawString(margin, y, "Configuration Steps:")
    y -= 20

    step_num = 1
    for step_text in config_steps:
        c.setFont("Helvetica-Bold", 12)
        c.drawString(margin, y, f"Step {step_num}:")
        y -= 16

        c.setFont("Helvetica", 12)
        c.drawString(margin + 20, y, step_text)
        y -= 20

        # Try inserting image for this step
        expected_filename = f"step{step_num}.png"
        if all_image_filenames and expected_filename in all_image_filenames:
            img_url = get_image_url(page_id, expected_filename)
            img_stream = download_image(img_url)
            if img_stream:
                try:
                    c.drawImage(ImageReader(img_stream), margin, y - 180, width=300, preserveAspectRatio=True, mask='auto')
                    y -= 200
                except Exception as e:
                    print(f"⚠️ Failed to draw step image: {e}")

        step_num += 1

        if y < 150:
            c.showPage()
            y = height - margin

    # Footer
    c.setFont("Helvetica", 8)
    c.setFillColor(colors.gray)
    c.drawCentredString(width / 2, 30, f"© {date.today().year} ACME Corp – Internal Use Only")

    c.save()
    buffer.seek(0)

    return buffer







