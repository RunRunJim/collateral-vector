import openai
import os
from dotenv import load_dotenv
import re
load_dotenv()

# Load the OpenAI API key from environment variables
openai.api_key = os.getenv("OPENAI_API_KEY")


def generate_summary_and_steps(full_text):
    prompt = f"""
You're a product enablement expert. Read the feature guidance below and do the following:

1. **Summarise the feature** in 100 words or fewer for internal commercial stakeholders. Focus on the client benefit and overall impact — not technical detail.
2. **Extract any setup or configuration instructions** from the text. These may appear under headings like "How to set up", "Configuration", "Steps", or similar. If found, return each step on a new line.

Format your output like this:

Feature Summary:
<your summary>

Configuration Steps:
- <step 1>
- <step 2>
...

If no configuration steps exist, just write "None" under that section.

Text:
\"\"\"{full_text}\"\"\"
"""

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=1000
        )
        return response['choices'][0]['message']['content'].strip()
    except Exception as e:
        print(f"Error generating AI output: {e}")
        return None
def generate_summary(brief):
    prompt = f"""
    You're a product enablement expert. Summarize this feature in 100 words or less for internal stakeholders...

    Brief:
    {brief}
    """

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        max_tokens=500
    )

    return response['choices'][0]['message']['content'].strip()
def generate_summary_and_significance(full_text):
    prompt = f"""
    You are a product enablement expert. Based on the following feature guidance:

    1. Write a 'Summary' paragraph in UK English  (max 60 words) explaining the new feature's purpose and benefit.
    2. Write an 'Improvement Significance' paragraph in UK English (max 60 words) explaining why this enhancement matters to users or clients.

    Feature Guidance:
    \"\"\"{full_text}\"\"\"
    """

    try:
        import openai
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.6,
            max_tokens=500
        )
        output_text = response['choices'][0]['message']['content'].strip()

        # 👇 Split the AI output manually
        if "Improvement Significance:" in output_text:
            summary_part, significance_part = output_text.split("Improvement Significance:")
            summary_text = summary_part.replace("Summary:", "").strip()
            improvement_text = significance_part.strip()
        else:
            # fallback if AI didn't format correctly
            summary_text = output_text
            improvement_text = ""

        return summary_text, improvement_text

    except Exception as e:
        print(f"❌ AI generation error: {e}")
        return "", ""

def generate_chat_reply(question, context_text):
    prompt = f"""
You are an expert support assistant for a software company. A user is asking a question about a product feature described below. Use the feature information to answer clearly and helpfully.

Feature Guidance:
\"\"\"{context_text}\"\"\"

User Question:
\"\"\"{question}\"\"\"

Answer:
"""

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5,
            max_tokens=500
        )
        return response['choices'][0]['message']['content'].strip()
    except Exception as e:
        print("⚠️ Chat error:", e)
        return "⚠️ Something went wrong while trying to answer your question."
import openai
import os
import re
from dotenv import load_dotenv

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")


from utils.confluence import get_image_url

def generate_release_note(template_text, feature_title, feature_text, config_steps, page_id, overview_image, all_image_filenames):
    release_note = ""

    feature_name = f"ABC-{feature_title}"

    feature_text_lower = feature_text.lower()

    editions = []
    if "reward centre" in feature_text_lower:
        editions.append("Reward Centre")
    if "control centre" in feature_text_lower:
        editions.append("Control Centre")
    editions_text = ", ".join(editions)

    languages_supported = ""
    if "language" in feature_text.lower():
        languages_supported = "Mention of languages found in feature guidance."
    else:
        languages_supported = ""

    jira_match = re.search(r'https:\/\/[^\s]+atlassian\.net\/browse\/[A-Z]+-\d+', feature_text)
    jira_link = jira_match.group(0) if jira_match else ""

    # Pull overview image if available
    overview_img_md = ""
    if overview_image:
        overview_img_url = get_image_url(page_id, overview_image)
        overview_img_md = f"\n\n![Overview Image]({overview_img_url})\n\n"

    # Build config steps with matching images
    config_text = ""
    if config_steps:
        for idx, step in enumerate(config_steps, start=1):
            step_line = f"- {step['text']}"
            expected_image_name = f"step{idx}.png"
            if expected_image_name in all_image_filenames:
                step_img_url = get_image_url(page_id, expected_image_name)
                step_line += f"\n  ![Step {idx}]({step_img_url})"
            config_text += step_line + "\n"
    else:
        config_text = "No configuration required."

    # AI Generated sections (Summary, Client Benefit, Origin)
    try:
        summary_prompt = f"""Summarize the following feature focusing on what it does in 2-3 sentences:

\"\"\"{feature_text}\"\"\"
"""
        summary_response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": summary_prompt}],
            temperature=0.5,
            max_tokens=300
        )
        summary_text = summary_response['choices'][0]['message']['content'].strip()

        benefit_prompt = f"""Based on the following feature, explain in 1-2 sentences how this feature benefits clients:

\"\"\"{feature_text}\"\"\"
"""
        benefit_response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": benefit_prompt}],
            temperature=0.5,
            max_tokens=300
        )
        benefit_text = benefit_response['choices'][0]['message']['content'].strip()

        origin_prompt = f"""Based on the feature guidance below, is the feature origin user feedback, client request, roadmap, research, or UX initiative? Reply with one of those or 'Unknown'.

\"\"\"{feature_text}\"\"\"
"""
        origin_response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": origin_prompt}],
            temperature=0.5,
            max_tokens=100
        )
        origin_text = origin_response['choices'][0]['message']['content'].strip()

    except Exception as e:
        print(f"⚠️ AI generation error: {e}")
        summary_text = "Summary not available."
        benefit_text = "Benefit not available."
        origin_text = "Origin not determined."

    # ✅ Build the final structured release note with images
    release_note = f"""

**Summary:**  
{summary_text}
{overview_img_md}

**Client Benefit:**  
{benefit_text}

**Origin of the Feature:**  
{origin_text}

**Editions Affected:**  
{editions_text or "None specified."}

**How is it Configured:**  
{config_text}

**Languages Supported:**  
{languages_supported or "Not specified."}

**Technical Details:**  
{jira_link or "Not available."}
"""

    feature_name = f"ABC - {feature_title.strip()}"

    return release_note.strip(), feature_name
def generate_custom_document(user_prompt, context_text):
    prompt = f"""
You are a product documentation assistant. 
The user is usually preparing internal materials like talking points, FAQs, client summaries, or bullet points.

Guidelines:
- Never format the response as an email or letter unless specifically requested.
- Do NOT include greetings, sign-offs, or "Dear..." lines unless you have been requested to create an email or letter.
- Respond with clear headings, bullet points, or numbered lists.
- Stay concise and direct.

You have the following Feature Guidance to reference:
\"\"\"{context_text}\"\"\"

The user's request is:
\"\"\"{user_prompt}\"\"\"

Generate a clean, structured document:
"""
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.6,
            max_tokens=1200
        )
        return response['choices'][0]['message']['content'].strip()
    except Exception as e:
        print(f"Error generating custom document: {e}")
        return "⚠️ Unable to generate document. Please try again."





