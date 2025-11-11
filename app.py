import streamlit as st
import time
import google.generativeai as genai
import os
import re # Added re for placeholder URL replacement
import base64 # --- ADDED: For logo encoding ---

# --- NEW: Function to encode logo ---
def get_image_as_base64(file_path):
    """Reads an image file and returns it as a base64 encoded data URI."""
    try:
        with open(file_path, "rb") as img_file:
            return f"data:image/jpeg;base64,{base64.b64encode(img_file.read()).decode()}"
    except FileNotFoundError:
        # --- CHANGED: Make error visible to user ---
        st.error(f"Logo file '{file_path}' not found. Please ensure 'StartWiseLogo.jpeg' is in the same directory as 'app.py'.")
        return "" # Return empty string on error

# Get the base64 string for the logo
LOGO_FILE = "StartWiseLogo.jpeg"
logo_base64 = get_image_as_base64(LOGO_FILE)


# --- 1. CONFIGURATION AND STYLING (MIMICKING APPLE/TAILWIND) ---

# The core CSS block to inject. This sets the dark mode theme,
# uses the Inter font (a common choice for modern, clean UI),
# and provides custom classes for the Apple-like components.
APPLE_TAILWIND_CSS = """
<style>
    /* 1. Global Setup (Dark Mode and Font) */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@100..900&display=swap');
    
    html, body, [data-testid="stAppViewContainer"] {
        background-color: #000000; /* Pure Black for contrast */
        color: #FFFFFF;
        font-family: 'Inter', sans-serif;
    }
    
    /* Center the main container content and maximize width */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1200px !important;
    }

    /* 2. Custom Typography and Layout */
    .apple-hero-title {
        font-size: 4rem;
        font-weight: 700;
        line-height: 1.1;
        /* text-align: center; <-- CHANGED */
        text-align: left; 
        /* margin-bottom: 1rem; <-- CHANGED */
        margin-bottom: 0;
        background: linear-gradient(180deg, #FFFFFF, #B0B0B0);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    .apple-hero-subtitle {
        font-size: 1.5rem;
        font-weight: 400;
        text-align: center;
        color: #888888;
        margin: 0 auto 3rem auto;
    }
    
    /* --- NEW: Hero container with logo --- */
    .apple-hero-container {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 1.5rem; /* Space between logo and text */
        margin-bottom: 1rem;
    }
    
    .apple-hero-container img {
        width: 90px;
        height: 90px;
        border-radius: 12px; 
        flex-shrink: 0; /* Prevent logo from shrinking */
    }

    .apple-page-title {
        font-size: 3rem;
        font-weight: 700;
        line-height: 1.2;
        margin-bottom: 2rem;
        text-align: center;
    }

    /* 3. Card/Navigation Styling (Minimalist) - Kept for future use if needed */
    .apple-card {
        background-color: #1a1a1a;
        border-radius: 12px;
        padding: 30px;
        margin-bottom: 20px;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.2);
        cursor: pointer;
    }
    
    .apple-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 20px rgba(0, 0, 0, 0.5);
    }
    
    /* 4. Default Button Styling (Pill shape) - Now used for nav */
    div.stButton > button {
        background-color: #1a1a1a; 
        color: #FFFFFF;
        border: 1px solid #333333;
        border-radius: 9999px; /* Pill shape */
        padding: 10px 20px;
        font-size: 1rem;
        font-weight: 500;
        transition: background-color 0.2s, border-color 0.2s;
        cursor: pointer;
    }

    div.stButton > button:hover {
        background-color: #333333;
        border-color: #555555;
    }
    
    /* 5. NEW Horizontal Navigation Bar */
    .apple-nav-container {
        width: 100%;
        border-bottom: 1px solid #2a2a2a; /* Subtle separator */
        margin-bottom: 3rem;
        padding: 0.5rem 0; /* Updated padding */
        background-color: #101010; /* Dark "strip" background */
        border-radius: 12px; /* Rounded corners */
    }
    
    /* Style for the buttons within the nav */
    .apple-nav-container [data-testid="stButton"] > button {
        background: none !important;
        border: none !important;
        color: #888888 !important; /* Inactive link color */
        padding: 5px 10px !important;
        font-size: 0.95rem; /* Slightly smaller */
        font-weight: 500;
        text-align: center;
        width: 100%;
    }

    .apple-nav-container [data-testid="stButton"] > button:hover {
        color: #FFFFFF !important; /* White on hover */
        background: none !important;
        border: none !important;
    }
    
    /* Style for the *disabled* (active) button */
    .apple-nav-container [data-testid="stButton"] > button:disabled {
        font-weight: 600; /* Bolder */
        color: #FFFFFF !important; /* Active link color */
        background: none !important;
        border: none !important;
        cursor: default !important;
    }

    /* 6. Form Element Styling */
    [data-testid="stTextInput"] > div > div > input,
    [data-testid="stTextArea"] > div > div > textarea {
        background-color: #1a1a1a;
        color: #FFFFFF;
        border: 1px solid #333333;
        border-radius: 8px; /* Slightly less rounded than pills */
        padding: 12px 15px;
        font-size: 1rem;
        font-family: 'Inter', sans-serif;
    }
    
    [data-testid="stTextArea"] > div > div > textarea {
        min-height: 100px; /* Specific to text area */
    }

    /* NEW: Style for placeholders */
    [data-testid="stTextInput"] > div > div > input::placeholder,
    [data-testid="stTextArea"] > div > div > textarea::placeholder {
        color: #777777;
        font-size: 0.9rem;
        font-style: italic;
    }

    /* Style for text input labels */
    [data-testid="stTextInput"] label,
    [data-testid="stTextArea"] label {
        color: #AAAAAA;
        font-weight: 500;
        padding-bottom: 5px;
        font-size: 1.3rem !important; /* Increased font size again to make it obvious */
    }

    /* 7. Primary Action Button (for 'Generate') - Primary Style */
    .apple-primary-button-container div.stButton > button {
        background-color: #007AFF !important; /* Apple Blue */
        color: #FFFFFF !important;
        border: none !important;
        border-radius: 9999px; /* Pill shape */
        padding: 12px 28px;
        font-size: 1.1rem;
        font-weight: 600;
        transition: background-color 0.2s;
        width: auto; /* Allow it to size to content */
        margin-top: 1.5rem;
    }
    
    .apple-primary-button-container div.stButton > button:disabled {
        background: #333 !important; /* Disabled grey */
        color: #FFFFFF !important;
        border: none !important;
    }

    .apple-primary-button-container div.stButton > button:hover {
        background-color: #0056b3 !important; /* Darker blue on hover */
        color: #FFFFFF !important;
        border: none !important;
    }
    
    /* 8. Input Summary Styling */
    .input-summary-section {
        background-color: #101010; /* Darker than output */
        border: 1px solid #2a2a2a;
        border-radius: 12px;
        padding: 1.5rem 2rem;
        margin-bottom: 1.5rem;
    }
    .input-summary-section h3 {
        font-size: 1rem;
        font-weight: 600;
        color: #AAAAAA; /* Grey label */
        margin-bottom: 0.5rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .input-summary-section p {
        font-size: 1.1rem;
        color: #E0E0E0;
        line-height: 1.6;
        font-style: italic;
        /* Use pre-wrap to respect newlines in the input */
        white-space: pre-wrap;
        word-wrap: break-word;
    }

    /* 9. Output Display Styling */
    .brand-output-section {
        background-color: #1a1a1a;
        border-radius: 12px;
        padding: 2rem 2.5rem;
        margin-top: 2rem;
        border: 1px solid #2a2a2a;
    }

    .brand-output-section h2 {
        font-size: 1.5rem;
        font-weight: 600;
        color: #FFFFFF;
        border-bottom: 1px solid #333;
        padding-bottom: 0.5rem;
        margin-bottom: 1.5rem;
    }

    .brand-output-section p {
        font-size: 1rem;
        color: #E0E0E0;
        line-height: 1.6;
        word-wrap: break-word; /* Added for long string wrapping */
        overflow-wrap: break-word; /* Added for long string wrapping */
    }
    
    .brand-output-section pre {
        white-space: pre-wrap; /* Ensure text wraps */
        word-wrap: break-word; /* Break long words */
        background-color: #080808; /* Slightly darker */
        padding: 1.5rem;
        border-radius: 8px;
        color: #E0E0E0;
        font-family: 'Menlo', 'Consolas', monospace;
        font-size: 0.95rem;
        line-height: 1.7;
    }
    
    /* NEW: Styling for markdown generated by the new prompt */
    .brand-output-section h3 {
        font-size: 1.25rem;
        font-weight: 600;
        color: #FFFFFF;
        margin-top: 2rem;
        margin-bottom: 0.5rem;
        border-bottom: 1px solid #333;
        padding-bottom: 0.5rem;
    }
    
    .brand-output-section h4 {
        font-size: 1.1rem;
        font-weight: 600;
        color: #E0E0E0;
        margin-top: 1.5rem;
        margin-bottom: 0.5rem;
    }
    
    .brand-output-section ul {
        list-style-type: disc;
        margin-left: 20px;
        padding-left: 0;
        color: #E0E0E0;
    }
    
    .brand-output-section li {
        margin-bottom: 0.5rem;
        line-height: 1.6;
        word-wrap: break-word; /* Added for long string wrapping */
        overflow-wrap: break-word; /* Added for long string wrapping */
    }

    .brand-output-section img {
        border-radius: 8px;
        margin-top: 1rem;
        max-width: 300px;
        border: 1px solid #333;
    }

    /* NEW: Styling for tables to prevent overflow */
    .brand-output-section table {
        display: block; /* Makes the table scrollable */
        width: 100%;
        overflow-x: auto; /* Adds horizontal scroll if needed */
        border-collapse: collapse;
        margin-top: 1rem;
        margin-bottom: 1rem;
        border: 1px solid #333; /* Border to match theme */
        border-radius: 8px; /* Match other elements */
    }

    .brand-output-section th,
    .brand-output-section td {
        border-bottom: 1px solid #333; /* Cell borders */
        padding: 0.75rem 1rem; /* Spacing */
        color: #E0E0E0;
        white-space: nowrap; /* Prevents text from wrapping and breaking layout */
        border-left: 1px solid #333;
    }
    
    .brand-output-section td:first-child,
    .brand-output-section th:first-child {
        border-left: none; /* Remove double border on the left */
    }

    .brand-output-section th {
        background-color: #2a2a2a; /* Header background */
        font-weight: 600;
        text-align: left;
    }
    
    .brand-output-section tr:first-child th:first-child {
        border-top-left-radius: 7px; /* Rounded corner */
    }
    .brand-output-section tr:first-child th:last-child {
        border-top-right-radius: 7px; /* Rounded corner */
    }


    /* Hide default Streamlit Chrome for a cleaner look */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
"""

# --- NEW: Logo Button Style ---
# We inject this dynamically after the main CSS block
LOGO_BUTTON_STYLE = f"""
<style>
    /* --- NEW: Style for the Home Logo Button (targets first column) --- */
    .apple-nav-container [data-testid="stColumn"]:first-child [data-testid="stButton"] > button {{
        background-image: url("{logo_base64}");
        
        /* --- KEPT: 'contain' is correct to fit without distortion --- */
        background-size: contain; 
        
        background-repeat: no-repeat;
        background-position: center;
        color: transparent !important; /* Hide the text "Home" */
        width: 100%; /* Use full column width */
        height: 40px; /* Set a fixed height */
        border: none !important;
        
        /* --- ADDED: Fallback color if image fails to load --- */
        background-color: #2a2a2a !important; 
        
        padding: 0 !important;
    }}
    
    .apple-nav-container [data-testid="stColumn"]:first-child [data-testid="stButton"] > button:hover {{
        /* --- CHANGED: Added fallback color --- */
        background-color: #333333 !important; /* Darker hover */
        opacity: 0.8; /* Add hover effect to image */
        color: transparent !important;
        border: none !important;
    }}
    
    .apple-nav-container [data-testid="stColumn"]:first-child [data-testid="stButton"] > button:disabled {{
        /* --- CHANGED: Added fallback color --- */
        background-color: #2a2a2a !important; /* Same as default */
        opacity: 1.0; /* Full opacity when active */
        color: transparent !important;
        border: none !important;
        cursor: default !important;
    }}
</style>
"""

# Apply the custom CSS at the start
st.set_page_config(layout="wide", page_title="Brand Generator App")
st.markdown(APPLE_TAILWIND_CSS, unsafe_allow_html=True)
# --- ADDED: Inject the logo style ---
if logo_base64: # Only inject if logo was found
    st.markdown(LOGO_BUTTON_STYLE, unsafe_allow_html=True)

# --- 2. GEMINI API CONFIGURATION ---

# Configure the API key from Streamlit secrets
try:
    # API_KEY = st.secrets["GEMINI_API_KEY"] # Replaced secret with hardcoded key
    API_KEY = "AIzaSyA2KlGc_qfH1GsSgiPL1CmUZIEyC12BIvc"
    genai.configure(api_key=API_KEY)
    # model = genai.GenerativeModel("gemini-2.5-flash-preview-09-2025") # Removed: Model will be initialized in each function
    GEMINI_ENABLED = True
except Exception as e:
    # Updated error message
    st.error(f"Error configuring Gemini API: {e}. Please check the API key.")
    GEMINI_ENABLED = False

# The prompt template to be filled by user inputs
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
2. Output both analytical and creative persona details. **IMPORTANT: For the 'Generated Persona Image', do NOT generate an image. Instead, use a descriptive placeholder URL from 'https://placehold.co/300x300/E0E0E0/000000?text=Persona+Name'**, replacing 'Persona+Name' with the actual persona's name (e.g., Aarav+K).

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
* **Generated Persona Image:** [Use the https://placehold.co URL as specified in the objectives]
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
Return your answer using clean, readable Markdown (headings, bullets) for clarity and embed the placeholder image URLs directly.
---
### Constraints
* Keep it concise, practical, and realistic to the Indian market.
* Use INR and Asia/Kolkata context.
* Avoid generic phrasing; show behavioral, digital, and cultural nuance relevant to the user's idea.
"""

# --- NEW: TLPrompt (Target Lens Prompt) ---
TL_PROMPT_TEMPLATE = """
You are a Competitive Intelligence and Marketing Landscape Analyst with access to data APIs (Similarweb, Crayon, Relevance AI).
Your goal:
To deliver a comprehensive, insight-driven competitor landscape report based on the provided startup context.
---
### STARTUP CONTEXT (Input)
{segmentation_data}
---
### YOUR TASK
Based *only* on the context above (startup idea, target market, personas), generate the following competitive analysis:

Step 1 | Competitor Identification
* Identify 5–7 direct and indirect competitors in the same product category and geography.
* Mention each brand’s focus (e.g., RTD coffee, café chain, functional beverage).
* Add URLs or handles where possible.
* If data is unavailable, infer logically and mark “(assumed).”

Step 2 | Competitor Landscape Summary
For each competitor, compile:
* Brand Positioning (how they describe themselves)
* Price Tier (₹ range or value vs premium)
* Distribution Channels (retail, q-commerce, D2C, marketplaces)
* Digital Presence (traffic volume, sources, geography via Similarweb)
* Marketing Messaging (themes, tone, creative slogans from Crayon)
* Ad and Content Clusters (visual tone + sentiment using Relevance AI)
* Differentiators / Innovations (unique value props, packaging, etc.)
* **give this summary in form of a table**

Step 3 | Market & Category Insights
* Identify key trends and consumer behaviors using Relevance AI or Similarweb data (e.g., search interest, engagement growth).
* Summarize market trajectory (growing / maturing / fragmented).
* Highlight 3 whitespace areas where existing players underperform.

Step 4 | Deeper Digital & Creative Intelligence
Include if data is available:
* Comparative traffic benchmarks (top 3 competitors).
* Top traffic sources (Search / Social / Direct / Referral).
* Paid vs organic mix.
* Sentiment breakdown of top ad creatives (positive / neutral / negative).
* 3 emerging creative themes (e.g., “Clean Energy,” “Minimalist Lifestyle,” “Wellness + Craft”).

Step 5 | Strategic Implications for the Startup
Summarize:
* Key opportunities and threats from competitor scan.
* Potential differentiation levers (tone, channels, partnerships).
* Recommended price & distribution strategy.
* Early creative tone suggestion.

---
### Step 6: Generated Visuals
Based on all the analysis above, generate the following three images. Do not add any extra text, just the images.

1.  **Market Perceptual Map:** A 2x2 matrix for the competitor landscape (e.g., axes: Price vs. Niche).
2.  **Market Share Pie Chart:** An estimated market share pie chart for the identified competitors.
3.  **Sentiment Word Clouds:** Two simple word clouds, one for Positive and one for Negative customer sentiment.
---

### Step 7: Output Formatting (Text)
Return all text output from Steps 1-5 as plain text sections:
Competitor Landscape Overview:
<paragraph>
Competitor Snapshots:
<Brand> – <summary>
…
Market & Category Insights:
<paragraph>
Deeper Digital & Creative Intelligence:
<paragraph>
Strategic Implications:
<paragraph>

### Constraints
* Keep Indian market context (INR, Asia/Kolkata).
* Use realistic data and inferred logic when APIs don’t return live metrics.
* Maintain professional, insight-led tone.
* Output must be clean and ready for dashboard rendering.
"""

# --- NEW: Market Radar Prompt (MRPrompt1) ---
MR_PROMPT_TEMPLATE = """
You are a Brand Positioning & Targeting Strategist with access to GenAI and audience/data tools (Relevance AI, Meta Audience Insights, Google Ads, Similarweb) .

Your task:
Build a fully-formed Positioning & Targeting Strategy for the startup below, including actionable visuals that can be downloaded.

---

### Step 1 | Input Recap

Retrieve and summarize the following variables from the user's provided context:
Product Context: [E.g., RTD Beverage, D2C Apparel, B2B SaaS Tool]
Geography: [E.g., USA (California), India (Tier 1 Metros), Global]
Model: [E.g., B2C D2C + Retail, B2B Subscription]
Budget (Monthly Marketing): [E.g., ₹5,00,000, $50,000]
Target segments: [List the 2–3 prioritized segments identified in prior analysis]
Competitor Set: [List 3–5 direct and indirect competitors]
Category Drivers: [List 3–5 key factors influencing purchase decisions, e.g., Price, Speed, Sustainability]

---

### Step 2 | Audience Refinement (GenAI & Data)
For each target segment:
• Derive Audience DNA: demographics, top interests, reach/CPM, negative audiences  
• Estimate CPM/CPC, CTR, CVR (mark **ASSUMED** if no exact data)  
• Provide summary:  
  - Audience DNA paragraph  
  - Top 5 interests/keywords with source  
  - Estimated Reach, CPM (₹), CPC (₹), Channels  

Restrict at Step2 in this response. Don’t ask additional questions at the end.
"""


# --- 3. STATE AND NAVIGATION FUNCTIONS ---

PAGE_NAMES = {
    "Home": "main_page",
    "Segment View": "page_a", # Renamed from "Branding"
    "Target Lens": "page_b", # Renamed from "MacBook"
    "Market Radar": "page_c", # Renamed from "iPhone 16"
    "Roadmap": "page_d", # Renamed from "Watch X"
    "Pricing": "page_e", # Renamed from "AirPods Max"
}

# Initialize session state for page management
if 'current_page' not in st.session_state:
    st.session_state.current_page = PAGE_NAMES["Home"]
if 'startup_idea' not in st.session_state:
    st.session_state.startup_idea = None
# Renamed startup_values to startup_launch_plan for clarity
if 'startup_launch_plan' not in st.session_state:
    st.session_state.startup_launch_plan = None
if 'generating' not in st.session_state:
    st.session_state.generating = False
# NEW: Session state for generated outputs
if 'segmentation_output' not in st.session_state:
    st.session_state.segmentation_output = None
if 'target_lens_output' not in st.session_state:
    st.session_state.target_lens_output = None
# --- NEW: Session state for Market Radar ---
if 'market_radar_output' not in st.session_state:
    st.session_state.market_radar_output = None


def navigate_to(page_key):
    """Sets the current page in session state."""
    st.session_state.current_page = page_key

def create_main_navbar():
    """Creates the static horizontal navigation bar."""
    st.markdown('<div class="apple-nav-container">', unsafe_allow_html=True)
    # --- CHANGED: Column ratios to give logo less space ---
    cols = st.columns([1, 2, 2, 2, 2, 2])
    
    page_keys = list(PAGE_NAMES.keys()) # ["Home", "Branding", ...]
    page_values = list(PAGE_NAMES.values()) # ["main_page", "page_a", ...]
    
    with cols[0]:
        is_active = st.session_state.current_page == page_values[0]
        if st.button(page_keys[0], key="nav_home", disabled=is_active):
            navigate_to(page_values[0])
            st.rerun() # Use rerun for instant page switch
    
    with cols[1]:
        is_active = st.session_state.current_page == page_values[1]
        if st.button(page_keys[1], key="nav_branding", disabled=is_active): # Updated key (key name is internal, fine to keep)
            navigate_to(page_values[1])
            st.rerun()
                
    with cols[2]:
        is_active = st.session_state.current_page == page_values[2]
        if st.button(page_keys[2], key="nav_mac", disabled=is_active):
            navigate_to(page_values[2])
            st.rerun()

    with cols[3]:
        is_active = st.session_state.current_page == page_values[3]
        if st.button(page_keys[3], key="nav_iphone", disabled=is_active):
            navigate_to(page_values[3])
            st.rerun()
                
    with cols[4]:
        is_active = st.session_state.current_page == page_values[4]
        if st.button(page_keys[4], key="nav_watch", disabled=is_active):
            navigate_to(page_values[4])
            st.rerun()
                
    with cols[5]:
        is_active = st.session_state.current_page == page_values[5]
        if st.button(page_keys[5], key="nav_airpods", disabled=is_active):
            navigate_to(page_values[5])
            st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

# --- 3. PAGE CONTENT FUNCTIONS ---

def main_page():
    """The main landing page with the hero section and input form."""
    
    # --- REMOVED: Logo from homepage body ---
    
    create_main_navbar()
    
    # --- NEW: Hero section with Logo + Title ---
    logo_html = ""
    if logo_base64: # Only show logo if it loaded
        logo_html = f'<img src="{logo_base64}" alt="StartWise Logo">'
    
    st.markdown(f"""
    <div class="apple-hero-container">
        {logo_html}
        <div class="apple-hero-title">Build smarter, launch faster.</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown(
        '<p class="apple-hero-subtitle">Tell us what your brand stands for, and we’ll do the rest.</p>',
        unsafe_allow_html=True
    )
    
    # --- New Input Form ---
    with st.form(key="brand_form"):
        idea = st.text_area(
            "What idea do you have in mind?", 
            placeholder="What is your product or service? What makes your product unique? How will you sell it?",
            height=100
        )
        # Updated this section as requested
        launch_plan = st.text_area(
            "What are your thoughts on a launch plan?", 
            placeholder="Where are you launching first? Who is your ideal customer? Any constraints?",
            height=100
        )
        
        # --- CHANGED: Removed st.markdown wrapper divs ---
        # The primary button is now styled directly via the new CSS rule
        submitted = st.form_submit_button("Generate Brand Identity", type="primary", disabled=not GEMINI_ENABLED)

        if submitted:
            if not idea or not launch_plan:
                st.error("Please fill out both fields to generate your brand identity.")
            else:
                st.session_state.startup_idea = idea
                st.session_state.startup_launch_plan = launch_plan # Updated state variable
                st.session_state.generating = True # Flag to show spinner on next page
                
                # --- UPDATED: Clear all old outputs on new submission ---
                st.session_state.segmentation_output = None
                st.session_state.target_lens_output = None
                st.session_state.market_radar_output = None # --- NEW ---
                
                navigate_to(PAGE_NAMES["Segment View"]) # FIXED: Was "Branding"
                st.rerun()


# --- 4. GEMINI API CALL FUNCTION ---

def get_segmentation_output(idea, launch_plan):
    """
    Calls the Gemini API with the formatted segmentation prompt.
    """
    if not GEMINI_ENABLED:
        return "Error: Gemini API is not configured. Please check your API key."

    # --- ADDED: Initialize text model ---
    model = genai.GenerativeModel("gemini-2.5-flash-preview-09-2025")

    # Format the prompt with user inputs
    prompt = SEGMENTATION_PROMPT_TEMPLATE.format(idea=idea, launch_plan=launch_plan)
    
    try:
        # Generate content
        response = model.generate_content(prompt)
        # A simple regex to replace placeholder image prompts with actual placeholder images
        placeholder_url = "https://placehold.co/600x400/2a2a2a/808080?text=Persona+Image"
        cleaned_output = re.sub(
            r"\[Generate and embed the image here.*?\]",
            f"![Persona Image]({placeholder_url})",
            response.text
        )
        return cleaned_output
    except Exception as e:
        st.error(f"An error occurred while calling the Gemini API: {e}")
        return f"Error: Could not generate content. {e}"

# --- NEW: Target Lens Gemini Function ---
def get_target_lens_output(segmentation_data: str):
    """
    Calls the Gemini API with the Target Lens prompt, using segmentation
    data as context. Now returns both text and images.
    """
    if not GEMINI_ENABLED:
        return {"text": "Error: Gemini API is not configured.", "images": []}
        
    # --- MODEL CHANGED HERE ---
    model = genai.GenerativeModel("gemini-2.5-flash-image-preview")
    
    # Format the prompt with the segmentation output
    prompt = TL_PROMPT_TEMPLATE.format(segmentation_data=segmentation_data)
    
    try:
        # --- GENERATION CALL CHANGED HERE ---
        # Removed the 'generation_config' with 'responseModalities' as it caused the error.
        # The 'gemini-2.5-flash-image-preview' model automatically handles multiple modalities.
        response = model.generate_content(prompt)
        
        # --- RESPONSE PROCESSING CHANGED HERE ---
        text_output = ""
        image_outputs = []
        
        if response.candidates and response.candidates[0].content and response.candidates[0].content.parts:
            for part in response.candidates[0].content.parts:
                if 'text' in part:
                    text_output += part.text + "\n"
                elif 'inlineData' in part:
                    img_data = part.inlineData
                    base64_data = img_data.data
                    mime_type = img_data.mimeType
                    image_url = f"data:{mime_type};base64,{base64_data}"
                    image_outputs.append(image_url)
                    
        return {"text": text_output, "images": image_outputs}

    except Exception as e:
        st.error(f"An error occurred while calling the Gemini API: {e}")
        return {"text": f"Error: Could not generate content. {e}", "images": []}

# --- NEW: Market Radar Gemini Function ---
def get_market_radar_output(segmentation_data: str):
    """
    Calls the Gemini API with the Market Radar (MR) prompt, using
    segmentation data as context. Returns text only.
    """
    if not GEMINI_ENABLED:
        return "Error: Gemini API is not configured. Please check your API key."

    # Initialize the text model
    model = genai.GenerativeModel("gemini-2.5-flash-preview-09-2025")
    
    # Format the prompt with the segmentation output
    prompt = MR_PROMPT_TEMPLATE.format(segmentation_data=segmentation_data)
    
    try:
        # Generate content
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        st.error(f"An error occurred while calling the Gemini API for Market Radar: {e}")
        return f"Error: Could not generate Market Radar content. {e}"


# --- 5. PAGE CONTENT FUNCTIONS ---

def page_a():
    """Segment View Page / Brand Output Page"""
    create_main_navbar()
    
    # Check if we landed here from the form
    if st.session_state.startup_idea and st.session_state.startup_launch_plan:
        st.markdown('<h1 class="apple-page-title">Segment View</h1>', unsafe_allow_html=True)
        
        # Display the inputs
        st.markdown(f"""
        <div class="input-summary-section">
            <h3>Startup Idea</h3>
            <p>"{st.session_state.startup_idea}"</p>
            <h3 style="margin-top: 1rem;">Launch Plan</h3>
            <p>"{st.session_state.startup_launch_plan}"</p>
        </div>
        """, unsafe_allow_html=True)
        
        output_placeholder = st.empty()
        
        # --- UPDATED: Generation block for all three APIs ---
        if st.session_state.generating:
            with st.spinner("Generating Brand Strategy (3 steps)..."):
                # 1. Call Segmentation API
                st.write("Step 1/3: Generating Market Segmentation...")
                segmentation_output = get_segmentation_output(
                    st.session_state.startup_idea, 
                    st.session_state.startup_launch_plan
                )
                st.session_state.segmentation_output = segmentation_output
                
                # Check if step 1 succeeded before proceeding
                if segmentation_output and not segmentation_output.startswith("Error:"):
                    # 2. Call Target Lens API
                    st.write("Step 2/3: Generating Competitive Analysis...")
                    target_lens_output = get_target_lens_output(segmentation_output)
                    st.session_state.target_lens_output = target_lens_output
                    
                    # 3. Call Market Radar API
                    st.write("Step 3/3: Generating Positioning Strategy...")
                    market_radar_output = get_market_radar_output(segmentation_output)
                    st.session_state.market_radar_output = market_radar_output
                    
                    st.write("Generation complete!")
                
                else:
                    # Handle segmentation error
                    st.error("Error during Step 1: Segmentation. Halting generation.")
                    st.session_state.target_lens_output = {"text": "Error: Could not generate Target Lens data because Segmentation failed.", "images": []}
                    st.session_state.market_radar_output = "Error: Could not generate Market Radar data because Segmentation failed."

                st.session_state.generating = False # Done generating
        
        # Display the generated output for *this page*
        if st.session_state.segmentation_output:
            output_placeholder.markdown(
                f'<div class="brand-output-section">{st.session_state.segmentation_output}</div>', 
                unsafe_allow_html=True
            )
        elif not st.session_state.generating:
             output_placeholder.error("There was an issue generating the segmentation output.")

    else:
        # Default content if no inputs
        st.markdown('<h1 class="apple-page-title">Segment View</h1>', unsafe_allow_html=True)
        st.markdown("## Define Your Identity.")
        st.markdown("""
            <p style="font-size: 1.1rem; color: #AAAAAA; margin-top: 2rem;">
            <i>To generate a brand identity, please return to the <b>Home</b> page and fill out the form.</i>
            </p>
        """, unsafe_allow_html=True)


def page_b():
    """Target Lens Page - NOW DYNAMIC with Text and Images"""
    create_main_navbar()
    st.markdown('<h1 class="apple-page-title">Target Lens</h1>', unsafe_allow_html=True)
    
    # Check if inputs exist
    if st.session_state.startup_idea and st.session_state.startup_launch_plan:
        # Display the inputs for context
        st.markdown(f"""
        <div class="input-summary-section">
            <h3>Startup Idea</h3>
            <p>"{st.session_state.startup_idea}"</p>
            <h3 style="margin-top: 1rem;">Launch Plan</h3>
            <p>"{st.session_state.startup_launch_plan}"</p>
        </div>
        """, unsafe_allow_html=True)
        
        output_placeholder = st.empty()
        
        # Check if the output for this page already exists
        if st.session_state.target_lens_output:
            # --- RENDER LOGIC CHANGED HERE ---
            output_data = st.session_state.target_lens_output
            text_output = output_data.get("text")
            image_output = output_data.get("images", [])

            with output_placeholder.container():
                if text_output:
                    st.markdown(
                        f'<div class="brand-output-section">{text_output}</div>', 
                        unsafe_allow_html=True
                    )
                
                if image_output:
                    st.markdown('<div class="brand-output-section" style="margin-top: 2rem;">', unsafe_allow_html=True)
                    st.markdown("<h3>Generated Visuals</h3>", unsafe_allow_html=True)
                    # Display images in columns for better layout
                    
                    # Ensure we have at least 1 column
                    num_cols = len(image_output) if len(image_output) > 0 else 1
                    cols = st.columns(num_cols)
                    
                    for i, img_url in enumerate(image_output):
                        # Use modulo for safety in case num_cols is 0, though we guard for it
                        with cols[i % num_cols]:
                            st.image(img_url, use_column_width=True)
                    st.markdown('</div>', unsafe_allow_html=True)
                
                if not text_output and not image_output:
                    st.warning("Generation complete, but no content was returned. The prompt might need adjustment.")
            # --- END OF RENDER LOGIC CHANGE ---
        
        # If it's currently generating, show a spinner
        elif st.session_state.generating:
             output_placeholder.info("Your analysis is being generated. Please wait...")
        # Fallback: If output doesn't exist but inputs do (e.g., error in first step)
        else:
            output_placeholder.warning("Could not find generated analysis. Please try submitting the form again from the Home page.")
            
    else:
        # Default content if no inputs
        st.markdown("## Analyze Your Competition.")
        st.markdown("""
            <p style="font-size: 1.1rem; color: #AAAAAA; margin-top: 2rem;">
            <i>To generate a competitive analysis, please return to the <b>Home</b> page and fill out the form.</i>
            </p>
        """, unsafe_allow_html=True)


def page_c():
    """--- NEW: Market Radar Page (Dynamic) ---"""
    create_main_navbar()
    st.markdown('<h1 class="apple-page-title">Market Radar</h1>', unsafe_allow_html=True)
    
    # Check if inputs exist
    if st.session_state.startup_idea and st.session_state.startup_launch_plan:
        # Display the inputs for context
        st.markdown(f"""
        <div class="input-summary-section">
            <h3>Startup Idea</h3>
            <p>"{st.session_state.startup_idea}"</p>
            <h3 style="margin-top: 1rem;">Launch Plan</h3>
            <p>"{st.session_state.startup_launch_plan}"</p>
        </div>
        """, unsafe_allow_html=True)
        
        output_placeholder = st.empty()
        
        # Check if the output for this page already exists
        if st.session_state.market_radar_output:
            output_placeholder.markdown(
                f'<div class="brand-output-section">{st.session_state.market_radar_output}</div>', 
                unsafe_allow_html=True
            )
        
        # If it's currently generating, show a spinner
        elif st.session_state.generating:
             output_placeholder.info("Your analysis is being generated. Please wait...")
        
        # Fallback: If output doesn't exist but inputs do (e.g., error in first step)
        else:
            output_placeholder.warning("Could not find generated analysis. Please try submitting the form again from the Home page.")
            
    else:
        # Default content if no inputs
        st.markdown("## Define Your Positioning.")
        st.markdown("""
            <p style="font-size: 1.1rem; color: #AAAAAA; margin-top: 2rem;">
            <i>To generate a positioning and targeting strategy, please return to the <b>Home</b> page and fill out the form.</i>
            </p>
        """, unsafe_allow_html=True)


def page_d():
    """Roadmap Page"""
    create_main_navbar()
    st.markdown('<h1 class="apple-page-title">Roadmap</h1>', unsafe_allow_html=True)
    st.markdown("## Reimagined. Revolutionary.")
    st.markdown("""
        <p style="font-size: 1.1rem; color: #E0E0E0;">
        Apple Watch X features an all-new design with a thinner case and a magnetic band attachment system. 
        It’s the essential tool for a healthy and active life.
        </p>
        <ul style="color: #E0E0E0; list-style-type: disc; margin-left: 20px; padding-left: 0;">
            <li>**S10 Chip:** Faster, more efficient processing.</li>
            <li>**Blood Glucose Monitoring:** Non-invasive monitoring capability.</li>
            <li>**New Health Sensors:** Advanced crash-detection.</li>
        </ul>
    """, unsafe_allow_html=True)

    
def page_e():
    """Pricing Page"""
    create_main_navbar()
    st.markdown('<h1 class="apple-page-title">Pricing</h1>', unsafe_allow_html=True)
    st.markdown("## Audio Purity. Redefined.")
    st.markdown("""
        <p style="font-size: 1.1rem; color: #E0E0E0;">
        AirPods Max deliver unparalleled high-fidelity audio with industry-leading Active Noise Cancellation. 
        They've been updated with USB-C and extended battery life.
        </p>
        <ul style="color: #E0E0E0; list-style-type: disc; margin-left: 20px; padding-left: 0;">
            <li>**H3 Chip:** Advanced computational audio processing.</li>
            <li>**Lossless Audio:** Support for high-resolution lossless audio.</li>
            <li>**New Carrying Case:** Ultra-low power mode for extended standby.</li>
        </ul>
    """, unsafe_allow_html=True)


# --- 6. MAIN APPLICATION LOGIC ---

page_functions = {
    PAGE_NAMES["Home"]: main_page,
    PAGE_NAMES["Segment View"]: page_a, # Updated
    PAGE_NAMES["Target Lens"]: page_b, # Updated
    PAGE_NAMES["Market Radar"]: page_c, # Updated
    PAGE_NAMES["Roadmap"]: page_d, # Updated
    PAGE_NAMES["Pricing"]: page_e, # Updated
}

# Execute the function corresponding to the current page state
page_functions[st.session_state.current_page]()
