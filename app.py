import streamlit as pd
import streamlit as st
import pandas as pd
from pydantic import BaseModel, Field
from google import genai
from google.genai import types

# Set up Streamlit Page Configuration
st.set_page_config(
    page_title="Gemini Stock Analysis Dashboard",
    page_icon="📈",
    layout="wide"
)

# App Title & Description
st.title("📈 Gemini Stock Analysis Dashboard")
st.markdown(
    "Analyze any stock ticker against a custom framework using **Gemini 2.5 Flash** with **Live Google Search Grounding**."
)

# 1. Sidebar - Configuration & API Key Input
st.sidebar.header("Configuration")
api_key = st.sidebar.text_input("Enter your Gemini API Key:", type="password")
st.sidebar.markdown(
    """
    [Get a Gemini API Key](https://aistudio.google.com/)
    
    **Google Sheet Framework Source:**
    [View Criteria Sheet](https://docs.google.com/spreadsheets/d/14657OFSdH5U0wHXYmrJYycHBsb-0Y8Xq5znHN5KU45A/edit?usp=sharing)
    """
)

# Public Google Sheet URL exported as CSV
SHEET_ID = "14657OFSdH5U0wHXYmrJYycHBsb-0Y8Xq5znHN5KU45A"
CSV_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv"

@st.cache_data(ttl=600)  # Cache framework for 10 minutes
def load_criteria_framework(url):
    try:
        df = pd.read_csv(url)
        # Ensure column names are stripped of whitespace
        df.columns = [col.strip() for col in df.columns]
        return df
    except Exception as e:
        st.error(f"Failed to load framework from Google Sheet: {e}")
        return None

# Load the criteria dataframe
criteria_df = load_criteria_framework(CSV_URL)

# 2. Main Interface - User Input
ticker = st.text_input("Enter Stock Ticker Symbol (e.g., AAPL, NVDA, TSLA):", "").upper().strip()

# Define Structured Output Schema for Gemini using Pydantic
class CriterionEvaluation(BaseModel):
    score: int = Field(description="A score from 1 to 10 evaluating how well the stock satisfies the criterion.")
    rationale: str = Field(description="Exactly a 2-sentence explanation justifying the score based on recent live search data.")

if ticker:
    if not api_key:
        st.warning("Please enter your Gemini API Key in the sidebar to run the analysis.")
    elif criteria_df is None or criteria_df.empty:
        st.error("Could not load criteria framework from Google Sheet. Please check the spreadsheet URL.")
    else:
        # Initialize Google GenAI client
        client = genai.Client(api_key=api_key)
        
        st.info(f"Analyzing framework for **{ticker}** using Gemini 2.5 Flash with Live Web Search...")
        
        evaluations = []
        progress_bar = st.progress(0)
        
        # Iterate over each row in the Google Sheet criteria
        for idx, row in criteria_df.iterrows():
            # Dynamically identify columns by position in case headers differ slightly
            criterion_name = row.iloc[0] # Column A
            weight = float(row.iloc[1])  # Column B
            instructions = row.iloc[2]  # Column C
            
            # Update user on progress
            st.write(f"🔍 Evaluating: **{criterion_name}**...")
            
            # Construct a prompt telling Gemini to use live search data
            prompt = f"""
            You are an expert financial analyst. Perform a live search query on the web to find the absolute most up-to-date data, financial metrics, and current news regarding the stock ticker '{ticker}'.
            
            Evaluate the stock ticker '{ticker}' specifically against this Criterion:
            Name: {criterion_name}
            Instruction: {instructions}
            
            Provide a score from 1 to 10 and exactly a 2-sentence rationale based on your search discoveries.
            """
            
            try:
                # Call Gemini 2.5 Flash using modern google-genai SDK
                response = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        # Enable real-time Google Search grounding
                        tools=[types.Tool(google_search=types.GoogleSearch())],
                        # Force Structured JSON Output matching our Pydantic schema
                        response_mime_type="application/json",
                        response_schema=CriterionEvaluation,
                        temperature=0.2
                    ),
                )
                
                # Parse the validated JSON output
                result = CriterionEvaluation.model_validate_json(response.text)
                
                evaluations.append({
                    "criterion": criterion_name,
                    "weight": weight,
                    "score": result.score,
                    "rationale": result.rationale
                })
                
            except Exception as e:
                st.error(f"Error evaluating '{criterion_name}': {e}")
                # Fallback to prevent app crash if a single call fails
                evaluations.append({
                    "criterion": criterion_name,
                    "weight": weight,
                    "score": 5,
                    "rationale": f"Failed to complete assessment due to an API error. ({e})"
                })
                
            # Advance progress bar
            progress_bar.progress((idx + 1) / len(criteria_df))
            
        progress_bar.empty()
        st.success("Analysis Complete!")
        
        # 3. Calculation & Top Performance Box Display
        total_weight = sum(item['weight'] for item in evaluations)
        weighted_score_sum = sum(item['score'] * item['weight'] for item in evaluations)
        final_weighted_score = weighted_score_sum / total_weight if total_weight > 0 else 0
        
        # Large Stat Box at the top
        st.markdown("---")
        col1, col2 = st.columns([1, 3])
        with col1:
            st.metric(
                label=f"FINAL WEIGHTED SCORE ({ticker})", 
                value=f"{final_weighted_score:.2f} / 10"
            )
        with col2:
            if final_weighted_score >= 8:
                st.success("🌟 Strong Recommendation: This stock scores exceptionally high across the core framework matrix.")
            elif final_weighted_score >= 6:
                st.info("⚖️ Moderate Recommendation: The stock performs well overall but presents notable trade-offs.")
            else:
                st.warning("⚠️ Caution: Weighted evaluations suggest elevated risks or weak performance on criteria constraints.")
                
        st.markdown("### Framework Breakdown")
        
        # 4. Display results inside clean visual card modules
        for item in evaluations:
            with st.container():
                st.markdown(
                    f"""
                    <div style="
                        border: 1px solid #e6e6e6; 
                        border-radius: 8px; 
                        padding: 15px; 
                        margin-bottom: 15px; 
                        background-color: rgba(28, 131, 225, 0.03);
                    ">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <h4 style="margin: 0; color: #1c83e1;">🎯 {item['criterion']}</h4>
                            <span style="font-size: 0.9em; font-weight: bold; background-color: #e1e4e8; padding: 3px 8px; border-radius: 4px;">
                                Weight: {item['weight']}
                            </span>
                        </div>
                        <p style="margin: 10px 0 5px 0; font-size: 1.1em;">
                            <strong>Score:</strong> <span style="font-size: 1.2em; color: #2e7d32; font-weight: bold;">{item['score']}/10</span>
                        </p>
                        <p style="margin: 0; color: #555; font-style: italic;">
                            <strong>Analysis:</strong> {item['rationale']}
                        </p>
                    </div>
                    """, 
                    unsafe_allow_html=True
                )
else:
    st.info("Please enter a stock ticker symbol above to generate your live analysis matrix.")
