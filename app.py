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
                if response and response.text:
                    return response.text
                else:
                    retries += 1
                    time.sleep(1)
                    continue
                
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
    if not text:
        return "3"
    match = re.search(r'\b(Phase\s*([1-5])|([1-5])\b)', text, re.IGNORECASE)
    if match:
        return match.group(2) if match.group(2) else match.group(3)
    return "3"  # Fallback baseline to Solid Growth if the text doesn't explicitly match

# Robust Smart Parsing Engine to capture data under any formatting variance
def parse_panel(text, start_tag, end_tag, fallback_header=None):
    if not text or not isinstance(text, str):
        return "⚠️ *Analysis data temporarily unavailable. Please rerun.*"
    
    # Clean up tags for matching flexibility
    clean_start = start_tag.replace("=", "").strip()
    clean_end = end_tag.replace("=", "").strip()
    
    # Strategy 1: Exact Match Pattern
    pattern = f"{re.escape(start_tag)}(.*?){re.escape(end_tag)}"
    match = re.search(pattern, text, re.DOTALL)
    if match:
        return match.group(1).strip()
        
    # Strategy 2: Fuzzy/Lenient Tag Matching (handles missing equals signs, casing changes)
    fuzzy_start = clean_start.replace("_", r"[\s_]*")
    fuzzy_end = clean_end.replace("_", r"[\s_]*")
    fuzzy_pattern = f"(?:===\s*)?{fuzzy_start}(?:\s*===)?(.*?)(?:===\s*)?{fuzzy_end}(?:\s*===)?"
    fuzzy_match = re.search(fuzzy_pattern, text, re.DOTALL | re.IGNORECASE)
    if fuzzy_match:
        return fuzzy_match.group(1).strip()
        
    # Strategy 3: Header-Based Splitting Fallback
    if fallback_header:
        header_pattern = f"({re.escape(fallback_header)}.*?)(?=\n###|\n===\s*PANEL|\Z)"
        header_match = re.search(header_pattern, text, re.DOTALL | re.IGNORECASE)
        if header_match:
            return header_match.group(1).strip()
            
    # Strategy 4: Raw Text Chunking Fallback (If structural tags failed entirely)
    if "PANEL_4" in start_tag or "PANEL_2" in start_tag:
        split_point = len(text) // 2
        return text[:split_point].strip() + "\n\n*(Note: Data recovered via structural backup layout parser)*"
    elif "PANEL_7" in start_tag or "PANEL_3" in start_tag:
        split_point = len(text) // 2
        return text[split_point:].strip() + "\n\n*(Note: Data recovered via structural backup layout parser)*"

    return text

# 4. User Input Interface (Updated for European Assets & Company Names)
with st.form(key="research_panel_form"):
    st.markdown("##### 🔍 Asset Selection")
    ticker = st.text_input(
        "Enter Company Name or Ticker Symbol:", 
        placeholder="e.g., Robot S.A., ASML, or EPA:OR"
    )
    
    # Clear, low-friction help text for European local listings
    st.caption(
        "💡 **Tip for European listings:** To ensure perfect data collection, provide the **full company name** "
        "or use the format from Google Finance (e.g., *EBR:UCB* for UCB or *AMS:ASML* for ASML)."
    )
    
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
        CRITICAL OPERATIONAL INSTRUCTION: You are a World-Class Strategic Analyst specialising in Business Lifecycle and Phase Identification. Your target stock identifier/company name is: '{ticker}'. 
        Step 1: Use your Google Search tool to identify today's current date and year.
        Step 2: Search SEC EDGAR, official Company Investor Relations pages, and recent financial filings to locate the most recent 10-K, 10-Q, or international Annual Reports for target '{ticker}'.
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
        CRITICAL OPERATIONAL INSTRUCTION: You are an elite hedge fund research engine. Perform a comprehensive analysis on target stock identifier/company name: '{ticker}'.
        Step 1: Use your Google Search tool to find today's current date/year.
        Step 2: Source recent regulatory filings (SEC EDGAR, European company registries, or investor relations centers) and earnings call transcripts.
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
            macro_analysis_output = None

    p2_output = parse_panel(macro_analysis_output, "=== PANEL_2_START ===", "=== PANEL_2_END ===", "# 🏰 MOAT ANALYSIS")
    p3_output = parse_panel(macro_analysis_output, "=== PANEL_3_START ===", "=== PANEL_3_END ===", "# 🚀 Future Growth Analysis")
    p5_output = parse_panel(macro_analysis_output, "=== PANEL_5_START ===", "=== PANEL_5_END ===", "# ⚠️ Execution Risk Analysis")
    p6_output = parse_panel(macro_analysis_output, "=== PANEL_6_START ===", "=== PANEL_6_END ===", "# 📊 Financial Health Analysis")

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
        CRITICAL OPERATIONAL INSTRUCTION: You are an expert financial analyst evaluating corporate fundamentals for target: '{ticker}' mapped against corporate lifecycle Phase: '{phase_num}'.
        Step 1: Use your Google Search tool to find today's current date and year.
        Step 2: Source recent filings (10-Q/10-K or international IR Annual Reports/investor presentations if non-US). Gather current share price, diluted share count, cash, debt, and consensus NTM (next-twelve-month) metrics. Calculate EV = Market Cap + Debt - Cash. Ensure currency consistency (e.g. convert to Euros if analyzing European operations).
        Step 3: Execute valuation models explicitly matching the Phase {phase_num} methodologies and industry overrides below.
        Step 4: Generate output using the exact layout below. Separate blocks with '---'. Do not add conversational intro text.

        ### VALUATION ALGORITHMIC FRAMEWORK BY LIFECYCLE PHASE
        - **Phase 1 (Startup):** Primary: FWD P/S (Guidance/Consensus). Secondary: P/GP. Peer set comparison.
        - **Phase 2 (Rapid Growth):** Primary: EV/Sales. Secondary: FWD P/S.
        - **Phase 3 (Solid Growth):** Primary: P/Sales. Secondary: EV/EBITDA (NTM).
        - **Phase 4 (Maturity):** Primary: Discounted Cash Flow (DCF) (5-10yr explicit + perpetuity). Secondary: FWD P/E.
        - **Phase 5 (Declining):** Primary: Sum-of-the-Parts (SOTP) / Net Asset Value (NAV). Secondary: Reverse DCF / Liquidation Value / Dividend Yield vs Risk-Free Rate.

        ### INDUSTRY / ASSAY-SPECIFIC OVERRIDES (Apply if company matches industry)
        - **Biotech / Life Sciences:** Probability-adjusted NPV (pNPV) of clinical pipeline using success probabilities. EV/Peak Sales. Green if Market Cap <= 0.7x pNPV; Yellow 0.7-1.3x; Red >= 1.3x.
        - **SaaS / Software:** Apply Rule of 40 (Growth % + FCF %). Evaluate EV/Gross Profit, FWD P/S, and Net Dollar Retention.
        - **Energy / Mining:** Net Asset Value (NAV/NPV) of reserves, SOTP by asset tier, EV/Reserves.
        - **Bitcoin / Crypto Treasury Companies:** Determine current market Net Asset Value (mNAV) and benchmark to peers.

        ### BENCHMARK COLOR RULES
        - 🟩 Green (Undervalued): Multiple <= peer 25th percentile OR <= company's own 3-year low. (Or unique industry tier match).
        - 🟨 Yellow (Within Normal Range / Fairly Valued): Multiple between peer 25th and 75th percentile.
        - 🟥 Red (Overvalued): Multiple >= peer 75th percentile OR >= company's 3-year high.

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
        - **Company:** {ticker}
        - **Phase:** {phase_num}
        - **Summary Valuation Rating:** [MANDATORY EVALUATION: State strictly as either **Undervalued 🟢**, **Fairly Valued 🟡**, or **Overvalued 🔴** based on the percentile comparison rules above]
        - **Target Phase Framework applied:** Valuation Method for Phase {phase_num} (plus any applicable Industry Override)
        - **Calculated Multiple / Model output:** [Provide exact multiple or valuation range, e.g., EV/Sales, Forward P/E, Reverse DCF intrinsic range, or pNPV calculations]
        - **Benchmark Sector Context:** [Provide explicit text evaluating current multiples relative to sector medians, peer distributions (25th/75th percentiles), and the company's 3-yr baseline to validate the summary rating]
        - **Key Drivers:** [List core components such as growth, margins, or risk trends moving this valuation]
        - **Sensitivity:** [Key assumptions that shift this valuation stance]

        ## 📎 Sources
        [1] Source Name (Filing/IR Report)
        [2] Source Name (Market Data/Consensus/Peer Medians)
        === PANEL_7_END ===
        """
        try:
            macro_val_output = generate_analysis_layer(ticker, metrics_valuation_prompt)
            p4_output = parse_panel(macro_val_output, "=== PANEL_4_START ===", "=== PANEL_4_END ===", "### 📊 Phase")
            p7_output = parse_panel(macro_val_output, "=== PANEL_7_START ===", "=== PANEL_7_END ===", "### 💰 Phase-Appropriate")
        except Exception as e:
            st.error(f"Error executing valuation modules: {e}")
            p4_output = "⚠️ Valuation metrics framework execution error."
            p7_output = "⚠️ Valuation calculation framework execution error."

    with st.expander("📊 Business Key Metrics Analysis", expanded=True):
        st.markdown(p4_output)

    with st.expander("💰 Business Valuation Analysis", expanded=True):
        st.markdown(p7_output)

    # ==================================================================
    # 🧠 PANEL #8: SYSTEM SYNTHESIS & SCORING ENGINE
    # ==================================================================
    # 1. Variable Extraction & Standardization
    try:
        current_phase = phase_output.strip().lower() if phase_output else "unknown"       
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
        CRITICAL OPERATIONAL INSTRUCTION: You are the Chief Investment Officer of a boutique equity fund specialising in microeconomic moats and structural corporate lifecycles. Your job is to specialise the data gathered across our research framework for target asset: '{ticker}' (Phase Context: Phase {phase_num}).

        The rules-based engine has already run a structural compliance check on this asset and determined the following mandatory designation:
        
        MANDATORY DESIGNATION: {calculated_status}
        SYSTEM REASONING: {rule_justification}

        You MUST accept this designation. Your role is to write the executive synthesis explaining the qualitative 'Why' behind this decision, utilizing the findings from our individual modules.

        CRITICAL ROUTING INSTRUCTIONS FOR INSIGHT GENERATION:
        Depending on the MANDATORY DESIGNATION provided above, adapt your breakdown inside the sections below using these parameters:

        1. If the status is "🚀 DEEP DIVE ASAP":
           - **Core Investment Thesis:** Strongly highlight exactly why this asset presents an exceptional opportunity (the microeconomic moats, lifecycle expansion momentum, and core drivers).
           - **Key Risks to Identify:** Explicitly map out the asymmetric blindspots, complex operational risk elements, or structural assumptions the analyst must verify or clear.

        2. If the status is "⏳ ADD TO WATCHLIST":
           - **Core Investment Thesis:** Explain what is structurally preventing this asset from unlocking an immediate Deep Dive recommendation right now (e.g., waiting on margin expansion, scale, market maturity, or missing micro-cap velocity).
           - **Key Risks to Identify:** Identify precisely what fundamental benchmark shifts, valuation thresholds, or corporate operational changes need to be met for this asset to become fully worthy of active investment attention.

        3. If the status is "❌ PASS":
           - **Core Investment Thesis:** Diagnose clearly whether the rejection is due to being too systemically or structurally risky (e.g., concentration issues, balance sheet distress) OR due to simply not being good enough from an expansion standpoint (e.g., stagnant revenue profiles, flatlining markets, weak phase dynamics).
           - **Key Risks to Identify:** Articulate the precise toxic flaw, cyclical decline mechanism, or competitive erosion hurdle that breaks the potential upside entirely.

        Output ONLY the markdown format below. Ensure the layout matches perfectly. Use the specific HTML structure provided below for the Final Recommendation to make it pop out with massive text and clear separation.

        # ⚖️ Assessment Summary: {ticker}
        <div style="background-color: rgba(255, 255, 255, 0.05); padding: 15px; border-left: 5px solid #ff4b4b; border-radius: 4px; margin: 15px 0;">
            <h2 style="margin: 0; padding: 0; font-size: 28px; font-weight: 800; letter-spacing: 0.5px;">
                Final Recommendation: {calculated_status}
            </h2>
        </div>

        **Core Investment Thesis (The \"Why\"):** [A punchy, single-sentence summary validating the system reasoning: '{rule_justification}']

        ### 📋 Core Investment Thesis & Risks
        - **Core Investment Thesis:** [Provide a detailed 2-3 sentence strategic rationale customized to the designation parameters specified above.]
        - **Key Risks to Identify:** [Provide a detailed 2-3 sentence breakdown customized to the designation parameters specified above.]

        ### 🛠️ Required Next Steps
        - **Primary Blindspot to Verify:** [Identify the #1 operational metric or data point needed to monitor this decision.]
        - **Trigger Condition:** [Define a clear operational or valuation trigger to either archive, monitor, or buy this stock.]
        """
        try:
            final_decision = generate_analysis_layer(ticker, p8_prompt)
            st.markdown(final_decision, unsafe_allow_html=True)
        except Exception as e:
            st.error(f"Error executing Panel 8 Logic Layer: {e}")

    st.close()
    st.success("✅ Full Framework Audit complete. Final recommendation engine active.")

# ------------------------------------------------------------------
# 🔄 RESET RUNTIME CONTROLS
# ------------------------------------------------------------------
st.write("---")
if st.button("🔄 Clear Dashboard & Run New Ticker"):
    st.rerun()
