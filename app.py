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
    /* 1. Global Setup (Light Mode and Font) */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@100..900&display=swap');
    body {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
        background-color: #FFFFFF; /* White background */
        color: #333333; /* Dark text */
    }
    .main {
        background-color: #FFFFFF; /* White main content area */
    }
    /* Hide Streamlit headers and footers */
    header, footer {
        visibility: hidden !important;
    }
    /* Custom Scrollbar */
    ::-webkit-scrollbar { width: 8px; }
    ::-webkit-scrollbar-track { background: #F0F0F0; }
    ::-webkit-scrollbar-thumb { background: #BBBBBB; border-radius: 4px; }
    ::-webkit-scrollbar-thumb:hover { background: #999999; }

    /* 2. Custom Apple-like Navigation Bar */
    .apple-navbar {
        display: flex;
        justify-content: space-between; /* Changed for logo + items */
        align-items: center;
        padding: 8px 16px;
        background-color: #F8F8F8; /* Light glassy background */
        border-bottom: 1px solid #E0E0E0; /* Subtle separator */
        margin-bottom: 24px;
        border-radius: 8px; /* Rounded corners for the bar */
    }
    .apple-logo-container { /* NEW */
        display: flex;
        align-items: center;
        gap: 10px; /* Space between logo and title */
    }
    .apple-logo { /* NEW */
        width: 32px; /* Logo size */
        height: 32px;
        border-radius: 4px; /* Slightly rounded logo */
    }
    .apple-logo-title { /* NEW */
        font-size: 1.25rem; /* 20px */
        font-weight: 600;
        color: #111111; /* Dark text */
        line-height: 1; /* Align text better */
    }
    .apple-nav-items { /* NEW: Container for nav items */
         display: flex;
         gap: 8px; /* Spacing between items */
    }
    .apple-nav-item {
        color: #333333; /* Dark text */
        background-color: transparent;
        border: none;
        padding: 8px 12px;
        border-radius: 6px;
        font-weight: 500;
        font-size: 0.95rem; /* 15px */
        text-decoration: none;
        transition: background-color 0.2s, color 0.2s;
        cursor: pointer;
        display: flex; /* For icon alignment */
        align-items: center; /* For icon alignment */
        gap: 6px; /* Space between icon and text */
    }
    .apple-nav-item:hover {
        background-color: #EFEFEF; /* Subtle light hover */
        color: #000000;
    }
    .apple-nav-item.active {
        background-color: #EBF5FF; /* Lighter Blue background */
        color: #0059B3; /* Darker blue text */
    }
    .apple-nav-item.active:hover {
        background-color: #DDEEFF; /* Slightly darker light blue on hover */
    }
    .apple-nav-item span { /* For emoji icons */
        font-size: 1.1rem;
    }
    /* Fallback for nav items when it's a button (from st.page_link) */
    button.apple-nav-item {
         color: #333333;
    }
    button.apple-nav-item:hover {
        color: #000000;
    }
    button.apple-nav-item.active {
        color: #0059B3;
    }

    /* 3. Custom Apple-like Cards */
    .apple-card {
        background-color: #FFFFFF; /* White card background */
        border-radius: 12px;
        padding: 24px;
        border: 1px solid #E5E5E5; /* Subtle border */
        margin-bottom: 16px;
        transition: box-shadow 0.3s;
    }
    .apple-card:hover {
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05); /* Subtle lift */
    }
    .apple-card h2 {
        font-size: 1.75rem; /* 28px */
        font-weight: 600;
        color: #111111;
        margin-top: 0;
        margin-bottom: 8px;
    }
    .apple-card p {
        font-size: 1.1rem; /* 17.6px */
        color: #555555; /* Medium grey for body */
        line-height: 1.6;
    }

    /* 4. Page Title */
    .apple-page-title {
        font-size: 2.5rem; /* 40px */
        font-weight: 700;
        color: #111111;
        margin-bottom: 24px;
        margin-top: 0px; /* Reset top margin */
    }

    /* 5. Streamlit Component Overrides */

    /* General Button */
    .stButton > button {
        background-color: #58A6FF; /* Lighter Blue */
        color: #FFFFFF;
        border: none;
        border-radius: 8px;
        padding: 10px 16px;
        font-weight: 600;
        font-size: 1rem;
        transition: background-color 0.2s;
    }
    .stButton > button:hover {
        background-color: #4A90E2; /* Darker light blue */
        color: #FFFFFF;
    }
    .stButton > button:focus {
        box-shadow: 0 0 0 3px rgba(88, 166, 255, 0.5); /* Focus ring */
    }

    /* Text Input */
    .stTextInput input[type="text"], .stTextInput input[type="password"] {
        background-color: #F8F8F8;
        color: #333333;
        border: 1px solid #CCCCCC;
        border-radius: 8px;
        padding: 10px 12px;
    }
    .stTextInput input[type="text"]:focus, .stTextInput input[type="password"]:focus {
        border-color: #58A6FF;
        box-shadow: 0 0 0 3px rgba(88, 166, 255, 0.5);
    }
    /* Placeholder text color */
    ::placeholder {
        color: #999999 !important;
        opacity: 1;
    }

    /* Chat Input */
    .stChatInput {
        background-color: #F8F8F8;
        border-top: 1px solid #E0E0E0;
    }
    .stChatInput input {
        background-color: #FFFFFF;
        color: #333333;
        border-radius: 8px;
        border: 1px solid #CCCCCC;
    }

    /* Chat Messages */
    [data-testid="chat-message-container"] {
        border-radius: 12px;
        padding: 16px;
        margin-bottom: 12px;
    }
    /* Assistant message */
    [data-testid="chat-message-container"]:not(:has(div[data-testid="chat-avatar-user"])) {
        background-color: #F0F0F0; /* Light grey */
    }
    /* User message */
    [data-testid="chat-message-container"]:has(div[data-testid="chat-avatar-user"]) {
        background-color: #EBF5FF; /* Lighter Blue */
        color: #111111; /* Dark text */
    }
    /* Make user message text dark */
    [data-testid="chat-message-container"]:has(div[data-testid="chat-avatar-user"]) p,
    [data-testid="chat-message-container"]:has(div[data-testid="chat-avatar-user"]) li {
        color: #111111;
    }
    /* Code blocks in chat */
    pre {
        background-color: #F8F8F8 !important; /* Light background */
        color: #333333 !important; /* Dark text */
        border: 1px solid #E0E0E0;
        border-radius: 8px;
        padding: 12px;
    }

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
