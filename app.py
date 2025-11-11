import streamlit as st
import time
import google.generativeai as genai
import os
import re
import base64

# --- Helpers ---------------------------------------------------------------

def get_image_as_base64(file_path):
    """Reads an image file and returns it as a base64 encoded data URI."""
    try:
        with open(file_path, "rb") as img_file:
            return f"data:image/jpeg;base64,{base64.b64encode(img_file.read()).decode()}"
    except FileNotFoundError:
        # Note: If StartWiseLogo.jpeg is not present, Streamlit will show an error, 
        # but the app will continue to run without the logo image.
        # st.error(f"Logo file '{file_path}' not found. Please ensure 'StartWiseLogo.jpeg' is in the same directory as 'app.py'.")
        return ""

def clean_model_markdown(text: str) -> str:
    """
    Cleanups for model output so we don't render stray HTML tags as text:
    - remove any lines that are just <div> or </div>
    - (safety) remove bare opening/closing div tags inline as well
    """
    # remove lines that only contain <div> or </div> (with optional spaces)
    text = re.sub(r"^\s*</?div>\s*$", "", text, flags=re.IGNORECASE | re.MULTILINE)
    # remove any stray standalone <div> / </div> that might appear inline
    text = re.sub(r"\s*</?div>\\s*", " ", text, flags=re.IGNORECASE)
    return text.strip()

# --- Branding assets -------------------------------------------------------

LOGO_FILE = "StartWiseLogo.jpeg"
logo_base64 = get_image_as_base64(LOGO_FILE)

# --- UI: CSS (NEW WHITE/DARK BLUE THEME) -----------------------------------

APPLE_TAILWIND_CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@100..900&display=swap');
    
    /* Page background and default text */
    html, body, [data-testid="stAppViewContainer"] {
        background-color: #FFFFFF; /* White */
        color: #333333; /* Dark text */
        font-family: 'Inter', sans-serif;
    }
    .block-container {
        padding-top: 0rem; /* Changed from 2rem to 0rem */
        padding-bottom: 2rem;
        max-width: 1200px !important;
    }
    
    /* Hero styles */
    .apple-hero-title {
        font-size: 4rem;
        font-weight: 700;
        line-height: 1.1;
        text-align: left;
        margin-bottom: 0;
        color: #0A2351; /* Dark Blue */
    }
    .apple-hero-subtitle {
        font-size: 1.5rem;
        font-weight: 400;
        text-align: center;
        color: #555555; /* Darker gray */
        margin: 0 auto 3rem auto;
    }
    .apple-hero-container {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 1.5rem;
        margin-bottom: 1rem;
    }
    .apple-hero-container img {
        width: 90px;
        height: 90px;
        border-radius: 12px;
        flex-shrink: 0;
    }
    .apple-page-title {
        font-size: 3rem;
        font-weight: 700;
        line-height: 1.2;
        margin-bottom: 2rem;
        text-align: center;
        color: #333333; /* Dark text */
    }
    
    /* Card styles */
    .apple-card {
        background-color: #F8F8F8; /* Light gray */
        border-radius: 12px;
        padding: 30px;
        margin-bottom: 20px;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05); /* Light shadow */
        cursor: pointer;
    }
    .apple-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 20px rgba(0, 0, 0, 0.1); /* Slightly stronger shadow */
    }
    
    /* Default button (secondary) */
    div.stButton > button {
        background-color: #FFFFFF; /* White */
        color: #0A2351; /* Dark Blue text */
        border: 1px solid #0A2351; /* Dark Blue border */
        border-radius: 9999px;
        padding: 10px 20px;
        font-size: 0.95rem;
        font-weight: 500;
        transition: background-color 0.2s, border-color 0.2s;
        cursor: pointer;
        white-space: nowrap;
    }
    div.stButton > button:hover {
        background-color: #F0F8FF; /* Very light blue */
        border-color: #003366; /* Darker blue */
    }
    
    /* Navbar */
    .apple-nav-container {
        width: 100%;
        border-bottom: 1px solid #000033; /* Darker blue border */
        margin-bottom: 3rem;
        padding: 0.5rem 0;
        background-color: #0A2351; /* Dark Blue */
        border-radius: 12px;
    }
    .apple-nav-container [data-testid="stButton"] > button {
        background: none !important;
        border: none !important;
        color: #A9B4C2 !important; /* Light gray-blue text */
        padding: 5px 10px !important;
        font-size: 0.95rem;
        font-weight: 500;
        text-align: center;
        width: 100%;
        white-space: nowrap;
    }
    .apple-nav-container [data-testid="stButton"] > button:hover {
        color: #FFFFFF !important; /* White */
        background: none !important;
        border: none !important;
    }
    /* Active/Disabled Navbar button styling (fixed) */
    .apple-nav-container [data-testid="stButton"] > button:disabled {
        font-weight: 600;
        color: #FFFFFF !important; /* White (active color) */
        background: #003366 !important; /* Slightly darker blue to highlight */
        border: none !important;
        cursor: default !important;
    }
    
    /* Inputs and Text Areas */
    [data-testid="stTextInput"] > div > div > input,
    [data-testid="stTextArea"] > div > div > textarea {
        background-color: #FFFFFF; /* White */
        color: #333333; /* Dark text */
        border: 1px solid #CCCCCC; /* Light gray border */
        border-radius: 8px;
        padding: 12px 15px;
        font-size: 0.85rem; /* Decreased font size from 1.5rem to 0.85rem (FIX) */
        font-family: 'Inter', sans-serif;
    }
    [data-testid="stTextArea"] > div > div > textarea {
        min-height: 100px;
    }
    [data-testid="stTextInput"] > div > div > input::placeholder,
    [data-testid="stTextArea"] > div > div > textarea::placeholder {
        color: #999999; /* Lighter gray placeholder */
        font-size: 0.9rem;
        font-style: italic;
    }
    [data-testid="stTextInput"] label,
    [data-testid="stTextArea"] label {
        color: #444444; /* Dark gray label */
        font-weight: 500;
        padding-bottom: 5px;
        font-size: 2rem !important;
    }
    
    /* Primary button (e.g., Generate) */
    .apple-primary-button-container div.stButton > button {
        background-color: #007AFF !important; /* Bright Blue */
        color: #FFFFFF !important; /* White */
        border: none !important;
        border-radius: 9999px;
        padding: 12px 28px;
        font-size: 1.1rem;
        font-weight: 600;
        transition: background-color 0.2s;
        width: auto;
        margin-top: 1.5rem;
    }
    .apple-primary-button-container div.stButton > button:disabled {
        background: #A9B4C2 !important; /* Light gray-blue */
        color: #EFEFEF !important;
        border: none !important;
    }
    .apple-primary-button-container div.stButton > button:hover {
        background-color: #0056b3 !important; /* Darker blue */
        color: #FFFFFF !important;
        border: none !important;
    }
    
/* Summary section (light gray box) - COMPACT VERSION */
.input-summary-section {
    background-color: #F8F8F8;
    border: 1px solid #E0E0E0;
    border-radius: 12px;
    padding: 1rem 1.5rem; /* CHANGED: Reduced padding */
    margin-bottom: 1.5rem; /* Kept this margin for spacing below the box */
}

.input-summary-section h3 {
    font-size: 0.9rem; /* CHANGED: Slightly smaller font */
    font-weight: 600;
    color: #555555;
    margin-bottom: 0.25rem; /* CHANGED: Reduced space below heading */
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.input-summary-section p {
    font-size: 1rem; /* CHANGED: Slightly smaller font */
    color: #333333;
    line-height: 1.4; /* CHANGED: Reduced line spacing */
    white-space: pre-wrap;
    word-wrap: break-word;
    font-style: italic;
}
    
    /* Main output section (white box) */
    .brand-output-section {
        background-color: #FFFFFF; /* White */
        border-radius: 12px;
        padding: 2rem 2.5rem;
        margin-top: 2rem;
        border: 1px solid #E0E0E0; /* Light border */
    }
    .brand-output-section h2 {
        font-size: 1.5rem;
        font-weight: 600;
        color: #0A2351; /* Dark Blue */
        border-bottom: 1px solid #E0E0E0; /* Light border */
        padding-bottom: 0.5rem;
        margin-bottom: 1.5rem;
    }
    .brand-output-section p {
        font-size: 1rem;
        color: #333333; /* Dark text */
        line-height: 1.6;
        word-wrap: break-word;
        overflow-wrap: break-word;
    }
    .brand-output-section pre {
        white-space: pre-wrap;
        word-wrap: break-word;
        background-color: #F8F8F8; /* Light gray */
        padding: 1.5rem;
        border-radius: 8px;
        color: #333333; /* Dark text */
        font-family: 'Menlo', 'Consolas', monospace;
        font-size: 0.95rem;
        line-height: 1.7;
    }
    .brand-output-section h3 {
        font-size: 1.25rem;
        font-weight: 600;
        color: #333333; /* Dark text */
        margin-top: 2rem;
        margin-bottom: 0.5rem;
        border-bottom: 1px solid #E0E0E0; /* Light border */
        padding-bottom: 0.5rem;
    }
    .brand-output-section h4 {
        font-size: 1.1rem;
        font-weight: 600;
        color: #444444; /* Dark gray */
        margin-top: 1.5rem;
        margin-bottom: 0.5rem;
    }
    .brand-output-section ul {
        list-style-type: disc;
        margin-left: 20px;
        padding-left: 0;
        color: #333333; /* Dark text */
    }
    .brand-output-section li {
        margin-bottom: 0.5rem;
        line-height: 1.6;
        overflow-wrap: break-word;
        word-wrap: break-word;
    }
    
    /* Table styles */
    .brand-output-section table {
        display: block;
        width: 100%;
        overflow-x: auto;
        border-collapse: collapse;
        margin-top: 1rem;
        margin-bottom: 1rem;
        border: 1px solid #E0E0E0; /* Light border */
        border-radius: 8px;
        table-layout: fixed;
    }
    .brand-output-section th,
    .brand-output-section td {
        border-bottom: 1px solid #E0E0E0;
        padding: 0.75rem 1rem;
        color: #333333; /* Dark text */
        white-space: normal !important;
        overflow-wrap: anywhere;
        vertical-align: top;
        border-left: 1px solid #E0E0E0;
    }
    .brand-output-section th:first-child,
    .brand-output-section td:first-child {
        min-width: 180px;
    }
    .brand-output-section th {
        background-color: #F8F8F8; /* Light gray header */
        font-weight: 600;
        text-align: left;
    }
    .brand-output-section tr:first-child th:first-child { border-top-left-radius: 7px; }
    .brand-output-section tr:first-child th:last-child  { border-top-right-radius: 7px; }

    /* Horizontal scroll wrapper */
    .table-scroll {
        overflow-x: auto;
        overflow-y: hidden;
        width: 100%;
        padding-bottom: 8px;
    }
    .table-scroll::-webkit-scrollbar { height: 8px; }
    .table-scroll::-webkit-scrollbar-thumb { background: #CCCCCC; border-radius: 4px; } /* Light gray thumb */
    .table-scroll::-webkit-scrollbar-track { background: #F8F8F8; } /* Light gray track */

    /* Hide Streamlit extras */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
"""

tabs_font_css = """
<style>
div[class*="stTextArea"] label {
  font-size: 26px;
  color: 0A2351;
}
</style>
"""

# Optional: convert the first nav button to a logo button if the logo exists.
LOGO_BUTTON_STYLE = f"""
<style>
    .apple-nav-container [data-testid="stColumn"]:first-child [data-testid="stButton"] > button {{
        {"background-image: url('" + logo_base64 + "');" if logo_base64 else ""}
        background-size: contain;
        background-repeat: no-repeat;
        background-position: center;
        width: 100%;
        height: 0px;
        border: none !important;
        padding: 0 !important;
        white-space: nowrap;
    }}
    .apple-nav-container [data-testid="stColumn"]:first-child [data-testid="stButton"] > button:hover {{
        background-color: #003366 !important; /* Darker blue on hover */
        opacity: 0.85;
        border: none !important;
    }}
    .apple-nav-container [data-testid="stColumn"]:first-child [data-testid="stButton"] > button:disabled {{
        background-color: #0A2351 !important; /* Match navbar blue */
        opacity: 1.0;
        border: none !important;
        cursor: default !important;
    }}
</style>
"""

st.set_page_config(layout="wide", page_title="SmartWise App")
st.markdown(APPLE_TAILWIND_CSS, unsafe_allow_html=True)
st.markdown(LOGO_BUTTON_STYLE, unsafe_allow_html=True)

# --- Gemini config ---------------------------------------------------------

try:
    # NOTE: Using a placeholder API key. In a real environment, this should be secured.
    API_KEY = "AIzaSyBKDZtEZf9LjlBnADcWBtoExM7-6LTZc0E" 
    genai.configure(api_key=API_KEY)
    GEMINI_ENABLED = True
except Exception as e:
    st.error(f"Error configuring Gemini API: {e}. Please check the API key.")
    GEMINI_ENABLED = False


# --- Prompts --------------------------------------------------------------

SEGMENTATION_PROMPT_TEMPLATE = """
You are a Startup Market Segmentation Expert with access to generative tools and data APIs.

---
### USER INPUTS
* **Startup Idea:** {idea}
* **Launch Plan:** {launch_plan}
---

Based on these inputs, generate a detailed market segmentation analysis.

### Your objectives:
1. Generate detailed target market and customer segmentation for the startup’s product idea.

---
### Step 1: Primary Target Market
Write one crisp sentence defining:
* The broad target market (country, demographics, psychographic need) based on the user's inputs.
---
### Step 2: Customer Segments (3–5)
For each segment, provide:
* **Segment Name:** Catchy but descriptive
* **Demographics:** Age, gender, income, geography
* **Psychographics:** Values, attitudes, lifestyle
* **Buying Motivations:** Key reasons to purchase
* **Pain Points / Unmet Needs:**
* **Channels & Media Preferences:** (Instagram, Blinkit, Zomato, LinkedIn, etc.)
* **Price Sensitivity:** High / Medium / Low
* **Fit with Brand:** High / Medium / Low
* **Persona Summary:** ≤80 words; written like a short story about this person’s daily life
Use realistic, India-specific details and current digital behavior cues based on the user's inputs.
---
### Step 3: Segment Prioritization
* Identify 1–2 high-priority segments to target first, and justify clearly.
* **Suggest the key marketing message or value proposition for them.**
---
### Step 4: Positioning Implication
* Define how the brand should position itself to attract these top segments.
* Suggest tone of voice and visual style cues for creatives.
---
### Step 5: Risks / Overlooked Audiences
* Highlight blind spots, compliance or regulatory concerns (e.g., FSSAI for beverages), and emerging opportunities.
---
### Step 6: Output Formatting
Return your answer using clean, readable Markdown (headings, bullets) for clarity. If you create tables, ensure they are valid Markdown tables.
---
### Constraints
* Keep it concise, practical, and realistic to the Indian market.
* Use INR and Asia/Kolkata context.
* Avoid generic phrasing; show behavioral, digital, and cultural nuance relevant to the user's idea.
"""

TL_PROMPT_TEMPLATE = """
You are a Competitive Intelligence and Marketing Landscape Analyst.

---
### STARTUP CONTEXT (Input)
{segmentation_data}
---
### YOUR TASK
Based *only* on the context above (startup idea, target market, personas), generate the following competitive analysis:

Step 1 | Competitor Identification
* Identify 5–7 direct and indirect competitors in the same product category and geography.
* Mention each brand’s focus (e.g., RTD coffee, café chain, functional beverage).
* Add URLs or handles where possible. If you infer, mark “(assumed).”

Step 2 | Competitor Landscape Summary (Table)
For each competitor, compile:
* Brand Positioning (self-description)
* Price Tier (₹ range or value vs premium)
* Distribution Channels (retail, q-commerce, D2C, marketplaces)
* Digital Presence (traffic source mix – inferred if needed)
* Marketing Messaging (themes, tone)
* Differentiators / Innovations

Step 3 | Market & Category Insights
* Key trends and consumer behaviors (reasonable inferences are fine).
* Market trajectory (growing / maturing / fragmented).
* 3 whitespace areas where players underperform.

Step 4 | Strategic Implications for the Startup
* Opportunities and threats.
* Potential differentiation levers (tone, channels, partnerships).
* Recommended price & distribution strategy.
* Early creative tone suggestion.

### Output Formatting (Text only)
Return clean Markdown with headings, bullets, and one summary table. No code blocks.
"""

MR_PROMPT_TEMPLATE = """
You are a Brand Positioning & Targeting Strategist.

---
### Step 1 | Input Recap
Summarize from context (reasonable inferences allowed):
- Product Context
- Geography
- Model
- Budget (Monthly Marketing) – mark ASSUMED if inferred
- Target segments (2–3 prioritized)
- Competitor set (3–5)
- Category drivers (3–5)

---
### Step 2 | Audience Refinement (Text only)
For each target segment:
• Audience DNA: demographics, top interests, negative audiences  
• Estimated CPM/CPC, CTR, CVR (mark **ASSUMED** if inferred)  
• Summary:
  - Audience DNA paragraph
  - Top 5 interests/keywords
  - Estimated Reach, CPM (₹), CPC (₹), Channels

Restrict at Step 2 in this response. Do not ask questions at the end.
"""

# NEW: Prompt template for image generation
ROADMAP_IMAGE_PROMPT_TEMPLATE = """
Based on the following strategic analysis context (Market Radar Report):
---
CONTEXT:
{market_radar_data}
---
Generate a high-level, visually clean, and professional strategic product roadmap visualization for the startup. The roadmap should represent key phases or milestones derived from the context (e.g., Q1: MVP Launch, Q2: Customer Acquisition, Q3: Expansion, etc.). The overall design must have a clean white background. Use clear, modern typography and a professional, startup-friendly aesthetic.
"""

# --- State -----------------------------------------------------------------

PAGE_NAMES = {
    "Home": "main_page",
    "Segment View": "page_a",
    "Target Lens": "page_b",
    "Market Radar": "page_c",
    "Roadmap": "page_d",
    "Pricing": "page_e",
}

if 'current_page' not in st.session_state:
    st.session_state.current_page = PAGE_NAMES["Home"]
if 'startup_idea' not in st.session_state:
    st.session_state.startup_idea = None
if 'startup_launch_plan' not in st.session_state:
    st.session_state.startup_launch_plan = None
if 'generating' not in st.session_state:
    st.session_state.generating = False
if 'segmentation_output' not in st.session_state:
    st.session_state.segmentation_output = None
if 'target_lens_output' not in st.session_state:
    st.session_state.target_lens_output = None
if 'market_radar_output' not in st.session_state:
    st.session_state.market_radar_output = None
# NEW: State for storing the generated roadmap image (base64)
if 'roadmap_image_output_base64' not in st.session_state:
    st.session_state.roadmap_image_output_base64 = None

# --- Navigation ------------------------------------------------------------

def navigate_to(page_key):
    st.session_state.current_page = page_key

def create_main_navbar():
    # FIX: Using st.columns([1, 1, 1, 1, 1, 1]) for equal spacing of 6 buttons
    cols = st.columns([1, 1, 1, 1, 1, 1]) 
    page_keys = list(PAGE_NAMES.keys())
    page_vals = list(PAGE_NAMES.values())

    for i in range(len(page_keys)):
        with cols[i]:
            is_active = st.session_state.current_page == page_vals[i]
            # FIX: Buttons are disabled only if they are the current page (highlighted)
            if st.button(page_keys[i], key=f"nav_{page_vals[i]}", disabled=is_active):
                navigate_to(page_vals[i]); st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

# --- Gemini calls --------------------------------------------------------

def get_segmentation_output(idea, launch_plan):
    if not GEMINI_ENABLED:
        return "Error: Gemini API is not configured. Please check your API key."

    model = genai.GenerativeModel("gemini-2.5-flash-preview-09-2025")
    prompt = SEGMENTATION_PROMPT_TEMPLATE.format(idea=idea, launch_plan=launch_plan)
    try:
        resp = model.generate_content(prompt)
        text = resp.text or ""
        return clean_model_markdown(text)
    except Exception as e:
        st.error(f"An error occurred while calling the Gemini API for Segmentation: {e}")
        return f"Error: Could not generate content. {e}"

def get_target_lens_output(segmentation_data: str):
    if not GEMINI_ENABLED:
        return "Error: Gemini API is not configured. Please check your API key."
    model = genai.GenerativeModel("gemini-2.5-flash-preview-09-2025")
    prompt = TL_PROMPT_TEMPLATE.format(segmentation_data=segmentation_data)
    try:
        resp = model.generate_content(prompt)
        return clean_model_markdown(resp.text or "")
    except Exception as e:
        st.error(f"An error occurred while calling the Gemini API for Target Lens: {e}")
        return f"Error: Could not generate content. {e}"

def get_market_radar_output(segmentation_data: str):
    if not GEMINI_ENABLED:
        return "Error: Gemini API is not configured. Please check your API key."
    model = genai.GenerativeModel("gemini-2.5-flash-preview-09-2025")
    prompt = MR_PROMPT_TEMPLATE.format(segmentation_data=segmentation_data)
    try:
        resp = model.generate_content(prompt)
        return clean_model_markdown(resp.text or "")
    except Exception as e:
        st.error(f"An error occurred while calling the Gemini API for Market Radar: {e}")
        return f"Error: Could not generate Market Radar content. {e}"

# NEW: Function to generate the roadmap image (Fixed for stability)
def get_roadmap_image_output(market_radar_data: str):
    if not GEMINI_ENABLED:
        return "Error: Gemini API is not configured."

    model_name = "gemini-2.5-flash-image-preview"
    model = genai.GenerativeModel(model_name)

    image_prompt = ROADMAP_IMAGE_PROMPT_TEMPLATE.format(market_radar_data=market_radar_data)

    # Function to generate text fallback
    def generate_text_fallback(data):
        st.warning("Visual roadmap generation failed. Generating a text-based fallback roadmap...")
        fallback_prompt = (
            "Based *only* on the CONTEXT below, output a structured text-based "
            "3-phase or 4-quarter roadmap (using markdown lists and headers) "
            "for the startup. Focus on logical next steps: MVP, Customer Acquisition, and Scaling. "
            "CONTEXT:\n---\n" + data
        )
        try:
            text_model = genai.GenerativeModel("gemini-2.5-flash-preview-09-2025")
            text_resp = text_model.generate_content(fallback_prompt)
            return "TEXT_FALLBACK::" + clean_model_markdown(text_resp.text or "Error: Could not generate a text fallback roadmap.")
        except Exception as fallback_e:
            st.error(f"Error generating text fallback: {fallback_e}")
            return f"Error: Could not generate a text fallback roadmap. {fallback_e}"


    try:
        # FIX: Removed the 'config' parameter and passed 'response_mime_type' directly as an argument
        # This resolves the "unexpected keyword argument 'config'" error.
        resp = model.generate_content(
            contents=[
                {"role": "user", "parts": [{"text": image_prompt}]}
            ],
            response_mime_type="image/jpeg"
        )

        # Check if the response structure is valid before accessing parts
        if (resp.candidates and 
            resp.candidates[0].content and 
            resp.candidates[0].content.parts and 
            len(resp.candidates[0].content.parts) > 0 and 
            resp.candidates[0].content.parts[0].inline_data and 
            resp.candidates[0].content.parts[0].inline_data.data):
            
            base64_data = resp.candidates[0].content.parts[0].inline_data.data
            return f"data:image/jpeg;base64,{base64_data}"
        else:
            # Case 1: Response returned, but no valid image data found (empty candidates/parts)
            return generate_text_fallback(market_radar_data)

    except Exception as e:
        st.error(f"An exception occurred during Gemini Image API call: {e}")
        # Case 2: An explicit exception occurred (e.g., timeout, network issue)
        return generate_text_fallback(market_radar_data)


# --- Pages -----------------------------------------------------------------

def main_page():
    create_main_navbar()
    logo_html = f'<img src="{logo_base64}" alt="StartWise Logo">' if logo_base64 else ""
    st.markdown(f"""
    <div class="apple-hero-container">
        {logo_html}
        <div class="apple-hero-title">Build smarter, launch faster.</div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown('<p class="apple-hero-subtitle">Tell us what your brand stands for, and we’ll do the rest.</p>', unsafe_allow_html=True)

    with st.form(key="brand_form"):
        idea = st.text_area("What idea do you have in mind?",
                            placeholder="What is your product or service? What makes it unique? How will you sell it?",
                            height=100)
        launch_plan = st.text_area("What are your thoughts on a launch plan?",
                                   placeholder="Where are you launching first? Who is your ideal customer? Any constraints?",
                                   height=100)

        st.markdown('<div class="apple-primary-button-container" style="display: flex; justify-content: center;">', unsafe_allow_html=True)
        submitted = st.form_submit_button("Let's Start!", type="primary", disabled=not GEMINI_ENABLED)
        st.markdown('</div>', unsafe_allow_html=True)

        if submitted:
            if not idea or not launch_plan:
                st.error("Please fill out both fields to generate your brand identity.")
            else:
                st.session_state.startup_idea = idea
                st.session_state.startup_launch_plan = launch_plan
                st.session_state.generating = True
                st.session_state.segmentation_output = None
                st.session_state.target_lens_output = None
                st.session_state.market_radar_output = None
                st.session_state.roadmap_image_output_base64 = None # Clear image state
                navigate_to(PAGE_NAMES["Segment View"])
                st.rerun()

def page_a():
    create_main_navbar()
    if st.session_state.startup_idea and st.session_state.startup_launch_plan:
        st.markdown('<h1 class="apple-page-title">Segment View</h1>', unsafe_allow_html=True)
        st.markdown(f"""
        <div class="input-summary-section">
            <h3>Startup Idea</h3>
            <p>"{st.session_state.startup_idea}"</p>
            <h3 style="margin-top: 1rem;">Launch Plan</h3>
            <p>"{st.session_state.startup_launch_plan}"</p>
        </div>
        """, unsafe_allow_html=True)

        output_placeholder = st.empty()

        if st.session_state.generating:
            with st.spinner("Generating Brand Strategy (4 steps)..."): # Updated step count to 4
                
                # --- Step 1: Segmentation ---
                st.write("Step 1/4: Generating Market Segmentation...")
                seg = get_segmentation_output(st.session_state.startup_idea, st.session_state.startup_launch_plan)
                st.session_state.segmentation_output = seg

                if seg and not seg.startswith("Error:"):
                    
                    # --- Step 2: Target Lens ---
                    st.write("Step 2/4: Generating Competitive Analysis (Target Lens)...")
                    tl = get_target_lens_output(seg)
                    st.session_state.target_lens_output = tl

                    if tl and not tl.startswith("Error:"): 
                        
                        # --- Step 3: Market Radar ---
                        st.write("Step 3/4: Generating Positioning Strategy (Market Radar)...")
                        mr = get_market_radar_output(seg)
                        st.session_state.market_radar_output = mr

                        if mr and not mr.startswith("Error:"): 
                            
                            # --- Step 4: Roadmap Image Generation (NEW) ---
                            st.write("Step 4/4: Generating Roadmap Visualization...")
                            image_loader = st.empty()
                            image_loader.info("Image generation can take up to 30 seconds...")

                            roadmap_image_data = get_roadmap_image_output(mr)
                            st.session_state.roadmap_image_output_base64 = roadmap_image_data
                            
                            image_loader.empty() # Clear loading message
                            
                            if roadmap_image_data and not (roadmap_image_data.startswith("Error:") or roadmap_image_data.startswith("TEXT_FALLBACK::")):
                                st.success("Generation complete! All analysis and the visual roadmap are ready.")
                            elif roadmap_image_data and roadmap_image_data.startswith("TEXT_FALLBACK::"):
                                st.warning("Visual roadmap generation failed. A text-based fallback roadmap was generated instead.")
                            else:
                                st.error("Error during Step 4: Roadmap Image Generation. Halting generation.")
                                st.session_state.roadmap_image_output_base64 = "Error: Image generation failed."
                        else:
                            st.error("Error during Step 3: Market Radar. Halting generation.")
                            st.session_state.market_radar_output = "Error: Market Radar generation failed."
                    else:
                        st.error("Error during Step 2: Target Lens. Halting generation.")
                        st.session_state.target_lens_output = "Error: Target Lens generation failed."
                else:
                    st.error("Error during Step 1: Segmentation. Halting generation.")

            st.session_state.generating = False
            st.rerun() # Rerun to ensure all pages update immediately with new data

        if st.session_state.segmentation_output:
            # FIX: Only output the segmentation markdown, removing the extra div tags outside
            output_placeholder.markdown(
                f'''
                <div class="brand-output-section">
                    <div class="table-scroll">
                        {st.session_state.segmentation_output}
                    </div>
                </div>
                ''',
                unsafe_allow_html=True
            )
        elif not st.session_state.generating:
            output_placeholder.error("There was an issue generating the segmentation output.")
    else:
        st.markdown('<h1 class="apple-page-title">Segment View</h1>', unsafe_allow_html=True)
        st.markdown("## Understand Your Market Segments.")
        st.markdown(
            '<p style="font-size: 1.1rem; color: #555555; margin-top: 2rem;"><i>Dive deep into detailed customer segments to tailor your offerings and maximize impact. To generate a market segments, please return to the <b>Home</b> page and fill out the form.</i></p>',
            unsafe_allow_html=True
        )

def page_b():
    create_main_navbar()
    st.markdown('<h1 class="apple-page-title">Target Lens</h1>', unsafe_allow_html=True)

    if st.session_state.startup_idea and st.session_state.startup_launch_plan:
        st.markdown(f"""
        <div class="input-summary-section">
            <h3>Startup Idea</h3>
            <p>"{st.session_state.startup_idea}"</p>
            <h3 style="margin-top: 1rem;">Launch Plan</h3>
            <p>"{st.session_state.startup_launch_plan}"</p>
        </div>
        """, unsafe_allow_html=True)

        output_placeholder = st.empty()

        if st.session_state.target_lens_output:
            text_output = st.session_state.target_lens_output
            output_placeholder.markdown(
                f'''
                <div class="brand-output-section">
                    <div class="table-scroll">
                        {text_output}
                    </div>
                </div>
                ''',
                unsafe_allow_html=True
            )
        elif st.session_state.generating:
            output_placeholder.info("Your analysis is being generated. Please wait...")
        else:
            output_placeholder.warning("Could not find generated analysis. Please try submitting the form again from the Home page.")
    else:
        st.markdown("## Analyze Your Competition.")
        st.markdown(
            '<p style="font-size: 1.1rem; color: #555555; margin-top: 2rem;"><i>To generate a competitive analysis, please return to the <b>Home</b> page and fill out the form.</i></p>',
            unsafe_allow_html=True
        )

def page_c():
    create_main_navbar()
    st.markdown('<h1 class="apple-page-title">Market Radar</h1>', unsafe_allow_html=True)

    if st.session_state.startup_idea and st.session_state.startup_launch_plan:
        st.markdown(f"""
        <div class="input-summary-section">
            <h3>Startup Idea</h3>
            <p>"{st.session_state.startup_idea}"</p>
            <h3 style="margin-top: 1rem;">Launch Plan</h3>
            <p>"{st.session_state.startup_launch_plan}"</p>
        </div>
        """, unsafe_allow_html=True)

        output_placeholder = st.empty()
        if st.session_state.market_radar_output:
            output_placeholder.markdown(
                f'<div class="brand-output-section">{st.session_state.market_radar_output}</div>',
                unsafe_allow_html=True
            )
        elif st.session_state.generating:
            output_placeholder.info("Your analysis is being generated. Please wait...")
        else:
            output_placeholder.warning("Could not find generated analysis. Please try submitting the form again from the Home page.")
    else:
        st.markdown("## Track Competitors and Trends.")
        st.markdown(
            '<p style="font-size: 1.1rem; color: #555555; margin-top: 2rem;"><i>Stay ahead with real-time insights on market dynamics, competitor moves, and emerging opportunities.</i></p>',
            unsafe_allow_html=True
        )

# UPDATED: page_d now displays the generated image
def page_d():
    create_main_navbar()
    st.markdown('<h1 class="apple-page-title">Roadmap</h1>', unsafe_allow_html=True)

    if st.session_state.startup_idea:
        st.markdown(f"""
        <div class="input-summary-section">
            <h3>Startup Idea</h3>
            <p>"{st.session_state.startup_idea}"</p>
            <h3 style="margin-top: 1rem;">Launch Plan</h3>
            <p>"{st.session_state.startup_launch_plan}"</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("## Strategic Product Roadmap Visualization")
        st.markdown("""
            <p style="font-size: 1.1rem; color: #555555; margin-bottom: 2rem;">
            This visual roadmap is dynamically generated by **Gemini-2.5-Flash-Image-Preview** based on the Market Radar report, 
            or a text fallback is provided if image generation fails.
            </p>
        """, unsafe_allow_html=True)

        if st.session_state.generating:
            st.info("The Roadmap content is currently being generated. Please wait...")
            
        elif st.session_state.roadmap_image_output_base64:
            output_content = st.session_state.roadmap_image_output_base64
            
            if output_content.startswith("TEXT_FALLBACK::"):
                # --- MODIFICATION: Display the pricing image ---
                # Check if the file exists in the root directory
                if os.path.exists("pricing.png"):
                    # Display the image, making it fit the column width
                    st.image("roadmap.png", use_column_width=True)
                else:
                    # Show a warning if the image is missing, but don't break the app
                    st.warning("Image 'pricing.png' not found. Please make sure it's in the root directory.")
                # --- END MODIFICATION ---
                # Display text fallback
                text_content = output_content.replace("TEXT_FALLBACK::", "")
                st.markdown(
                    f'''
                    <div class="brand-output-section">
                        <h4 style="color: #CC6600;">Text-Based Roadmap (Visual Generation Failed)</h4>
                        {text_content}
                    </div>
                    ''',
                    unsafe_allow_html=True
                )
            elif not output_content.startswith("Error:"):
                # Display successful image
                st.markdown(
                    f'''
                    <div class="brand-output-section" style="padding: 1rem; text-align: center;">
                        <img src="{output_content}" alt="Startup Roadmap Visualization" 
                            style="max-width: 100%; height: auto; border-radius: 8px; box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);">
                        <h4 style="margin-top: 1rem; color: #0A2351;">Visualizing your Path to Market Success</h4>
                    </div>
                    ''',
                    unsafe_allow_html=True
                )
            else:
                # Display explicit error
                st.error(f"Failed to generate Roadmap content: {output_content.replace('Error: ', '')}")
        else:
            st.warning("Roadmap analysis not available. Please go to the Home page and submit a brand idea to begin generation.")
    else:
        st.markdown("## Plan Your Startup’s Journey.")
        st.markdown(
            '<p style="font-size: 1.1rem; color: #555555; margin-top: 2rem;"><i>To generate a strategic roadmap, please return to the <b>Home</b> page and fill out the form.</i></p>',
            unsafe_allow_html=True
        )

def page_e():
    create_main_navbar()
    st.markdown('<h1 class="apple-page-title">Pricing</h1>', unsafe_allow_html=True)
    st.markdown("## Build Winning Pricing Models.")
    st.markdown("""
        <p style="font-size: 1.1rem; color: #333333;">
        Design flexible pricing strategies that align with your value proposition and market demand.
        They've been updated with USB-C and extended battery life.
        </p>
    """, unsafe_allow_html=True)
    # --- MODIFICATION: Display the pricing image ---
    # Check if the file exists in the root directory
    if os.path.exists("pricing.png"):
        # Display the image, making it fit the column width
        st.image("pricing.png", use_column_width=True)
    else:
        # Show a warning if the image is missing, but don't break the app
        st.warning("Image 'pricing.png' not found. Please make sure it's in the root directory.")
    # --- END MODIFICATION ---

# --- Router ----------------------------------------------------------------

page_functions = {
    PAGE_NAMES["Home"]: main_page,
    PAGE_NAMES["Segment View"]: page_a,
    PAGE_NAMES["Target Lens"]: page_b,
    PAGE_NAMES["Market Radar"]: page_c,
    PAGE_NAMES["Roadmap"]: page_d,
    PAGE_NAMES["Pricing"]: page_e,
}
page_functions[st.session_state.current_page]()
