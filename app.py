import streamlit as st
import re
import time
from google import genai
from google.genai import types
from google.genai.errors import APIError

# 1. Page Configuration & Styling
st.set_page_config(page_title="Equity Research Analyzer", layout="wide")
st.title("📊 Custom Equity Research Dashboard")
st.subheader("Run your proprietary investment framework instantly")

# 2. Securely Initialize Gemini Client
if "GEMINI_API_KEY" not in st.secrets:
    st.error("Error: GEMINI_API_KEY is missing from your Streamlit Advanced Settings / Secrets.")
    st.stop()

@st.cache_resource
def get_gemini_client():
    return genai.Client(api_key=st.secrets["GEMINI_API_KEY"])

client = get_gemini_client()

# 3. Optimized API Call Wrapper with Caching, Backoff Retries, and Model Fallbacks
@st.cache_data(show_spinner=False)
def generate_analysis_layer(ticker, prompt_text):
    config = types.GenerateContentConfig(
        tools=[{"google_search": {}}],
        temperature=0.2,
    )
    
    # Try the high-speed flash model first, fallback to pro if the flash pool is congested
    models_to_try = ["gemini-2.5-flash", "gemini-2.5-pro"]
    max_retries = 3
    
    for model_name in models_to_try:
        retries = 0
        while retries < max_retries:
            try:
                response = client.models.generate_content(
                    model=model_name, 
                    contents=prompt_text, 
                    config=config
                )
                return response.text
                
            except APIError as e:
                # Catch 503 (High Demand/Unavailable) or 429 (Rate Limits)
                if e.code in [503, 429]:
                    retries += 1
                    if retries < max_retries:
                        # Exponential backoff sleep: 2s, 4s, 8s
                        sleep_time = 2 ** retries 
                        time.sleep(sleep_time)
                        continue
                break
            except Exception:
                break
                
    # Ultimate exception fallback if both model infrastructure layers fail to respond
    raise RuntimeError("All upstream analysis engines are currently rate-limited or overloaded by Google. Please wait a moment and try again.")

# Helper function to extract the single digit phase number from the model's text output
def extract_phase_number(text):
    match = re.search(r'\b(Phase\s*([1-5])|([1-5])\b)', text, re.IGNORECASE)
    if match:
        return match.group(2) if match.group(2) else match.group(3)
    return "3"  # Fallback baseline to Solid Growth if the text doesn't explicitly match

# 4. User Input Interface
with st.form(key="research_panel_form"):
    ticker = st.text_input("Enter Stock Ticker Symbol (e.g., TSLA, ASML, NVDA):", "").strip().upper()
    submit_button = st.form_submit_button(label="🚀 Run Full Framework Audit")

# 5. Run Analysis Framework Upon Submission
if submit_button and ticker:
    st.info(f"Analyzing {ticker}... Pulling primary filings, establishing lifecycle phase, and processing framework panels.")

    # ==================================================================
    # 🧭 BATCH 1: Business Phase Analysis (The Core Foundation)
    # ==================================================================
    phase_output = ""
    with st.expander("🧭 Business Phase Analysis", expanded=True):
        st.write("*Fetching latest structural lifecycle positioning...*")
        p1_prompt = f"""
        CRITICAL OPERATIONAL INSTRUCTION: You are a World-Class Strategic Analyst specialising in Business Lifecycle and Phase Identification. Your target stock ticker is: '{ticker}'. 
        Step 1: Use your Google Search tool to identify today's current date and year.
        Step 2: Search SEC EDGAR, official Company Investor Relations pages, and recent financial filings to locate the most recent 10-K, 10-Q, or international Annual Reports for ticker '{ticker}'.
        Step 3: Analyze the company's trajectory, revenue patterns, and product maturity. Classify it strictly into one of the following 5 phases: 1. Startup, 2. Rapid Growth, 3. Solid Growth, 4. Maturity, 5. Declining.
        Step 4: Output your final findings using the template format below. Do not add any conversational preambles. Output ONLY the completed template. It is vital you include the exact phrase 'Phase X' (where X is 1-5) in your 'Identified Phase' field.

        # 🧭 Business Phase Analysis: [Company Name] ({ticker})
        **Identified Phase:** Phase [Phase Number]: [Phase Name]
        **Confidence Level:** [High / Medium / Low]

        ### 📊 Phase Diagnostic Matrix
        - **Revenue Growth Profile:** [Describe current trajectory vs historical baseline]
        - **Profitability & Cash Flows:** [Identify status of Net Income, Operating Margins, and FCF generation]
        - **Capital Allocation Trends:** [Note major behaviors like heavy R&D investment, aggressive M&A, share buybacks, or dividend payouts]

        ### 🔬 Phase Justification Narrative
        [Provide a clear, cohesive 2-3 sentence paragraph explaining precisely why the company fits into this specific lifecycle phase based on the financial evidence.]

        ## 🔗 Sources Used
        [1] [Exact name of core primary SEC filing or international IR report used]
        """
        try:
            phase_output = generate_analysis_layer(ticker, p1_prompt)
            st.markdown(phase_output)
        except Exception as e:
            st.error(f"Error executing Panel 1: {e}")
            phase_output = "Phase 3"

    # Automatically determine the phase from the response to route downstream configurations
    phase_num = extract_phase_number(phase_output)
    st.caption(f"🤖 System localized corporate baseline structure to: **Phase {phase_num}**")

    # ==================================================================
    # 🏎️ BATCH 2: Core Analysis Macro-Prompt (Moat, Growth, Risks, & Financials)
    # ==================================================================
    macro_analysis_output = ""
    with st.spinner("⚡ Running Deep-Search Core Analysis Engine (Processing Moats, Growth, Risks, and Statements)..."):
        macro_prompt = f"""
        CRITICAL OPERATIONAL INSTRUCTION: You are an elite hedge fund research engine. Perform a comprehensive analysis on target stock ticker: '{ticker}'.
        Step 1: Use your Google Search tool to find today's current date/year.
        Step 2: Source recent SEC EDGAR filings (10-K, 10-Q, 1A Risk Factors) and earnings call transcripts.
        Step 3: Generate the full analysis using the exact demarcated templates below. Separate components with the clear marker '---'. Do not include any conversational intro or outro.

        === PANEL_2_START ===
        # 🏰 MOAT ANALYSIS: [Company Name] ({ticker})
        **Moat size:** [Select one: None ❌, Narrow ➖, Moderate ⚖️, Wide ✅]
        **Moat direction:** [Select one: Widening ✅ / Stable ➖ / Narrowing ❌]
        **Primary moat sources:** [List the 1-2 most dominant moat sources]
        **Summary:** [Provide a 1-2 sentence summary of the Moat thesis, supported by a key metric citation.]

        ## 👥 NETWORK EFFECT
        **Assessment:** [Present ✅ / Not Present ❌]
        **Analysis:** [Provide reasoning for your network effect assessment.]

        ## ⚓ SWITCHING COSTS
        **Assessment:** [Present ✅ / Not Present ❌]
        **Analysis:** [Provide reasoning for your switching costs assessment.]

        ## 🏭 LOW-COST PRODUCTION
        **Assessment:** [Present ✅ / Not Present ❌]
        **Analysis:** [Provide reasoning for your low-cost production assessment.]

        ## 🚀 COUNTER POSITIONING
        **Assessment:** [Present ✅ / Not Present ❌]
        **Analysis:** [Provide reasoning for your counter positioning assessment.]

        ## 🏆 INTANGIBLE ASSETS
        **Assessment:** [Present ✅ / Not Present ❌]
        **Analysis:** [Provide reasoning for your intangible assets assessment.]
        === PANEL_2_END ===

        ---

        === PANEL_3_START ===
        # 🚀 Future Growth Analysis: [Company Name] ({ticker}) 
        **Growth Potential:** [Select one: High ✅ / Moderate ➖ / Low ❌] 
        **Growth Direction:** [Select one: Accelerating ✅ / Stable ➖ / Decelerating ❌] 
        **Evidence Summary:** [1–2 sentence narrative supported by a defining corporate growth metric citation.] 

        ## 🌍 Market Expansion
        **Assessment:** Strength: [🟢/🟡/🔴/⚫] | Direction: [✅/➖/❌]
        **Evidence:** [Data-driven narrative.] 

        ## 🧪 Product Innovation
        **Assessment:** Strength: [🟢/🟡/🔴/⚫] | Direction: [✅/➖/❌]
        **Evidence:** [Data-driven narrative.] 

        ## 🤖 Technology Adoption
        **Assessment:** Strength: [🟢/🟡/🔴/⚫] | Direction: [✅/➖/❌]
        **Evidence:** [Data-driven narrative.] 

        ## ⚖️ Regulatory Tailwinds
        **Assessment:** Strength: [🟢/🟡/🔴/⚫] | Direction: [✅/➖/❌]
        **Evidence:** [Data-driven narrative.] 
        === PANEL_3_END ===

        ---

        === PANEL_5_START ===
        # ⚠️ Execution Risk Analysis: [Company Name] ({ticker})
        ## 📊 Overall Summary
        - **Overall Risk Level:** [High Risk 🔴 / Medium Risk 🟡 / Low Risk 🟢]
        - **⚠️ Primary Risk Factors:** [List the highest risk pillars]
        - **🛡️ Key Mitigation:** [Highlight corporate defense program]

        ## 🎯 RISK ASSESSMENT DETAILS
        ### 🥚🧺 Concentration
        - **Rating:** [🔴/🟡/🟢] | **Trend:** [⬆️/➖/⬇️]
        - **Evidence:** [1 concise bullet point with inline filing citation]
        
        ### 🥷 Disruption
        - **Rating:** [🔴/🟡/🟢] | **Trend:** [⬆️/➖/⬇️]
        - **Evidence:** [...]

        ### 🕵️ Outside Forces
        - **Rating:** [🔴/🟡/🟢] | **Trend:** [⬆️/➖/⬇️]
        - **Evidence:** [...]

        ### 👥 Competition
        - **Rating:** [🔴/🟡/🟢] | **Trend:** [⬆️/➖/⬇️]
        - **Evidence:** [...]
        === PANEL_5_END ===

        ---

        === PANEL_6_START ===
        # 📊 Financial Health Analysis: [Company Name] ({ticker})
        ## ✅ Overall Summary
        - **Overall Financial Health:** [Strong / Moderate / Weak]
        
        ## 🔍 Detailed Analysis 
        ### 📋 Income Statement
        - **Revenue Trend:** [⬆️/➖/⬇️] | **Score:** [🔴/🟡/🟢] | *Evidence:* [Brief text with citation]
        - **Gross Profit Trend:** [⬆️/➖/⬇️] | **Score:** [🔴/🟡/🟢]
        - **Operating Income Trend:** [⬆️/➖/⬇️] | **Score:** [🔴/🟡/🟢]
        - **EPS Trend:** [⬆️/➖/⬇️] | **Score:** [🔴/🟡/🟢]

        ### 🏦 Balance Sheet
        - **Cash & Securities:** [⬆️/➖/⬇️] | **Score:** [🔴/🟡/🟢]
        - **Debt Levels:** [⬆️/➖/⬇️] | **Score:** [🔴/🟡/🟢]

        ### 💸 Cash Flows
        - **Free Cash Flow:** [⬆️/➖/⬇️] | **Score:** [🔴/🟡/🟢]
        - **Operating Cash Flow:** [⬆️/➖/⬇️] | **Score:** [🔴/🟡/🟢]
        === PANEL_6_END ===
        """
        try:
            macro_analysis_output = generate_analysis_layer(ticker, macro_prompt)
        except Exception as e:
            st.error(f"Error during macro batch execution: {e}")

    # Parse out individual panel strings from the single macro text response
    def parse_panel(text, start_tag, end_tag):
        pattern = f"{start_tag}(.*?){end_tag}"
        match = re.search(pattern, text, re.DOTALL)
        return match.group(1).strip() if match else "Analysis unavailable due to processing timeout."

    p2_output = parse_panel(macro_analysis_output, "=== PANEL_2_START ===", "=== PANEL_2_END ===")
    p3_output = parse_panel(macro_analysis_output, "=== PANEL_3_START ===", "=== PANEL_3_END ===")
    p5_output = parse_panel(macro_analysis_output, "=== PANEL_5_START ===", "=== PANEL_5_END ===")
    p6_output = parse_panel(macro_analysis_output, "=== PANEL_6_START ===", "=== PANEL_6_END ===")

    # Layout Design: Side-by-Side Panels for better space efficiency
    col1, col2 = st.columns(2)
    with col1:
        with st.expander("🏰 Moat Analysis v3", expanded=True):
            st.markdown(p2_output)
    with col2:
        with st.expander("🚀 Business Growth Analysis v2.2", expanded=True):
            st.markdown(p3_output)

    col3, col4 = st.columns(2)
    with col3:
        with st.expander("⚠️ Business Risk Analysis v2.0", expanded=True):
            st.markdown(p5_output)
    with col4:
        with st.expander("📊 Financial Statement Analysis v1.1", expanded=True):
            st.markdown(p6_output)

    # ==================================================================
    # 📈 BATCH 3: Dynamic Metrics & Valuation Layer (Panels 4 & 7 Combined)
    # ==================================================================
    p4_output = ""
    p7_output = ""
    with st.spinner(f"🔢 Running valuation math specifically targeted to Phase {phase_num}..."):
        metrics_valuation_prompt = f"""
        CRITICAL OPERATIONAL INSTRUCTION: You are an expert financial analyst evaluating corporate fundamentals for ticker: '{ticker}' mapped against corporate lifecycle Phase: '{phase_num}'.
        Step 1: Calculate core metrics and valuation models explicitly matching Phase {phase_num} methodologies.
        Step 2: Generate output using the exact layout below. Separate blocks with '---'. Do not add conversational intro text.

        === PANEL_4_START ===
        ### 📊 Phase {phase_num} Core Diagnostic Benchmarking
        | Metric Found | Actual Calculated Value | Benchmark Status (🔴/🟡/🟢) |
        | :--- | :--- | :--- |
        | Revenue Growth / Profile | [Value] | [🔴/🟡/🟢] |
        | Core Profitability Margin | [Value] | [🔴/🟡/🟢] |
        | Capital Efficiency Metric | [Value] | [🔴/🟡/🟢] |
        | Asset Health Allocation | [Value] | [🔴/🟡/🟢] |
        | Shareholder Alignment | [Value] | [🔴/🟡/🟢] |
        === PANEL_4_END ===

        ---

        === PANEL_7_START ===
        ### 💰 Phase-Appropriate Valuation Model Target
        - **Target Phase Framework applied:** Valuation Method for Phase {phase_num}
        - **Calculated Multiple / Model output:** [Provide exact multiple or valuation range, e.g., EV/Sales, Forward P/E, Reverse DCF intrinsic range]
        - **Benchmark Context:** [Compare against industry peer average thresholds]
        === PANEL_7_END ===
        """
        try:
            macro_val_output = generate_analysis_layer(ticker, metrics_valuation_prompt)
            p4_output = parse_panel(macro_val_output, "=== PANEL_4_START ===", "=== PANEL_4_END ===")
            p7_output = parse_panel(macro_val_output, "=== PANEL_7_START ===", "=== PANEL_7_END ===")
        except Exception as e:
            st.error(f"Error executing valuation modules: {e}")

    with st.expander("📊 Business Key Metrics Analysis", expanded=True):
        st.markdown(p4_output)

    with st.expander("💰 Business Valuation Analysis", expanded=True):
        st.markdown(p7_output)

    # ==================================================================
    # 🧠 PANEL #8: SYSTEM SYNTHESIS & SCORING ENGINE
    # ==================================================================
    # 1. Variable Extraction & Standardization
    try:
        current_phase = phase_output.strip().lower()       
        risk_level = p5_output.strip().lower()        
        growth_potential = p3_output.strip().lower()   
        is_small_cap = True  
    except Exception:
        current_phase = "unknown"
        risk_level = "unknown"
        growth_potential = "unknown"
        is_small_cap = True

    # 2. Strict Deterministic Rules Filter
    if "declining" in current_phase or "startup" in current_phase or "phase 1" in current_phase or "phase 5" in current_phase:
        calculated_status = "❌ PASS"
        rule_justification = "Company is currently classified within a structural Startup or Declining business phase."

    elif "high risk" in risk_level and "high" not in growth_potential:
        calculated_status = "❌ PASS"
        rule_justification = "The asset's high risk profile is unmitigated by an elite future growth runway."

    elif "moderate" in growth_potential or "low" in growth_potential:
        calculated_status = "❌ PASS"
        rule_justification = "Growth potential is moderate or low, failing to meet premium return thresholds."

    elif "rapid" in current_phase or "solid" in current_phase or "phase 2" in current_phase or "phase 3" in current_phase:
        if is_small_cap and ("high" in growth_potential or "accelerating" in growth_potential):
            calculated_status = "🚀 DEEP DIVE ASAP"
            rule_justification = "High-growth small-cap asset operating in a prime Rapid or Solid expansion lifecycle phase."
        else:
            calculated_status = "⏳ ADD TO WATCHLIST"
            rule_justification = "Solid fundamentals with high growth potential, but lacks the immediate micro-cap velocity required for an instant Deep Dive."

    else:
        calculated_status = "⏳ ADD TO WATCHLIST"
        rule_justification = "Cleared structural risk filters. Placed on watchlist for systematic monitoring."

    # 3. Panel UI Render & LLM Justification Injection
    with st.expander("⚖️ Panel #8: Final Investment Decision", expanded=True):
        st.write("*Synthesizing framework layers into a final allocation recommendation...*")
        
        p8_prompt = f"""
        CRITICAL OPERATIONAL INSTRUCTION: You are the Chief Investment Officer of a boutique equity fund specialising in microeconomic moats and structural corporate lifecycles. Your job is to specialise the data gathered across our research framework for ticker: '{ticker}' (Phase Context: Phase {phase_num}).

        The rules-based engine has already run a structural compliance check on this asset and determined the following mandatory designation:
        
        MANDATORY DESIGNATION: {calculated_status}
        SYSTEM REASONING: {rule_justification}

        You MUST accept this designation. Your role is to write the executive synthesis explaining the qualitative 'Why' behind this decision, utilizing the findings from our individual modules. Output ONLY the markdown format below.

        # ⚖️ Strategic Allocation Summary: {ticker}
        **Final Framework Recommendation:** {calculated_status}
        **Core Investment Thesis (The \"Why\"):** [A punchy, single-sentence summary validating the system reasoning: '{rule_justification}']

        ### 📋 Core Synthesis Matrix
        - **Moat & Growth Alignment:** [1-2 sentences explaining how the moat protects or fails to protect this specific growth lifecycle.]
        - **Financial Health vs. Valuation:** [1-2 sentences balancing the balance sheet against the current trading multiple.]
        - **Execution Risk Friction:** [1-2 sentences detailing the primary threat that validates our risk rating.]

        ### 🛠️ Required Next Steps
        - **Primary Blindspot to Verify:** [Identify the #1 operational metric or data point needed to monitor this decision.]
        - **Trigger Condition:** [Define a clear operational or valuation trigger to either archive, monitor, or buy this stock.]
        """
        try:
            final_decision = generate_analysis_layer(ticker, p8_prompt)
            st.markdown(final_decision)
        except Exception as e:
            st.error(f"Error executing Panel 8 Logic Layer: {e}")

    st.success("✅ Full Framework Audit complete. Final recommendation engine active.")

# ------------------------------------------------------------------
# 🔄 RESET RUNTIME CONTROLS
# ------------------------------------------------------------------
st.write("---")
if st.button("🔄 Clear Dashboard & Run New Ticker"):
    st.rerun()
