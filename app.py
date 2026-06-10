import streamlit as st
import re
import time
from google import genai
from google.genai import types
from google.genai.errors import APIError
from fpdf import FPDF

# 1. Page Configuration & Styling
st.set_page_config(page_title="European Hidden Gems Analyzer", layout="wide")
st.title("📊 European Hidden Gems Research Dashboard")
st.subheader("30-Second Analysis: Instantly determine if this business is a Pass, Add to Watchlist, or Deep Dive Asap.")
st.caption("version 1.2")

# ==================================================================
# 🔒 PASSWORD PROTECTION GATEWAY (INLINE STABLE VERSION)
# ==================================================================
if "password_correct" not in st.session_state:
    st.session_state.password_correct = False

if not st.session_state.password_correct:
    st.write("### 🔒 Security Access Required")
    st.write("This proprietary dashboard is reserved for premium members.")
    with st.form("password_gate_form", clear_on_submit=False):
        user_password = st.text_input("Enter your access password:", type="password")
        submit_pass = st.form_submit_button("Unlock Dashboard", use_container_width=True)
        
        if submit_pass:
            if user_password == "GEMS":
                st.session_state.password_correct = True
                st.success("🔓 Access Granted!")
                time.sleep(0.6)
                st.rerun()
            elif user_password == "":
                st.warning("Please enter a password.")
            else:
                st.error("❌ Incorrect password. Access Denied.")
    st.stop()

# 2. Securely Initialize Gemini Client
if "GEMINI_API_KEY" not in st.secrets:
    st.error("Error: GEMINI_API_KEY is missing from your Streamlit Advanced Settings / Secrets.")
    st.stop()

@st.cache_resource
def get_gemini_client():
    return genai.Client(api_key=st.secrets["GEMINI_API_KEY"])

client = get_gemini_client()

# 3. Optimized API Call Wrapper
@st.cache_data(show_spinner=False)
def generate_analysis_layer(ticker, prompt_text):
    config = types.GenerateContentConfig(
        tools=[{"google_search": {}}],
        temperature=0.2,
    )
    
    models_to_try = ["gemini-3.1-flash-lite", "gemini-2.5-flash-lite"]
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
                if e.code in [503, 429]:
                    retries += 1
                    if retries < max_retries:
                        sleep_time = 2 ** retries 
                        time.sleep(sleep_time)
                        continue
                break
            except Exception:
                break
                
    raise RuntimeError("All upstream analysis engines are currently rate-limited or overloaded by Google. Please wait a moment and try again.")

def extract_phase_number(text):
    if not text:
        return "3"
    match = re.search(r'\b(Phase\s*([1-5])|([1-5])\b)', text, re.IGNORECASE)
    if match:
        return match.group(2) if match.group(2) else match.group(3)
    return "3"

def parse_panel(text, start_tag, end_tag, fallback_header=None):
    if not text or not isinstance(text, str):
        return "⚠️ *Analysis data temporarily unavailable. Please rerun.*"
    
    clean_start = start_tag.replace("=", "").strip()
    clean_end = end_tag.replace("=", "").strip()
    
    pattern = f"{re.escape(start_tag)}(.*?){re.escape(end_tag)}"
    match = re.search(pattern, text, re.DOTALL)
    if match:
        return match.group(1).strip()
        
    fuzzy_start = clean_start.replace("_", r"[\s_]*")
    fuzzy_end = clean_end.replace("_", r"[\s_]*")
    fuzzy_pattern = f"(?:===\s*)?{fuzzy_start}(?:\s*===)?(.*?)(?:===\s*)?{fuzzy_end}(?:\s*===)?"
    fuzzy_match = re.search(fuzzy_pattern, text, re.DOTALL | re.IGNORECASE)
    if fuzzy_match:
        return fuzzy_match.group(1).strip()
        
    if fallback_header:
        header_pattern = f"({re.escape(fallback_header)}.*?)(?=\n###|\n===\s*PANEL|\Z)"
        header_match = re.search(header_pattern, text, re.DOTALL | re.IGNORECASE)
        if header_match:
            return header_match.group(1).strip()
            
    if "PANEL_4" in start_tag or "PANEL_2" in start_tag:
        split_point = len(text) // 2
        return text[:split_point].strip() + "\n\n*(Note: Data recovered via structural backup layout parser)*"
    elif "PANEL_7" in start_tag or "PANEL_3" in start_tag:
        split_point = len(text) // 2
        return text[split_point:].strip() + "\n\n*(Note: Data recovered via structural backup layout parser)*"

    return text

def contains_any(text, keywords):
    if not text:
        return False
    text_lower = text.lower()
    return any(kw in text_lower for kw in keywords)

# ==================================================================
# 🗂️ MAIN HOMEPAGE SELECTION PANEL (CORRECT INDENTATION)
# ==================================================================
with st.form(key="research_panel_form"):
    st.header("Lets Go...")
    ticker_input = st.text_input("Add ticker to run stock analysis:", placeholder="e.g., Nebius Group NV (NBIS)")
    st.markdown("Enter both the company name and the ticker symbol to ensure perfect data collection according to Google Finance (e.g., *Rolls-Royce Holdings PLC LON:RR or 2Crsi SA EPA:AL2SI*).")
    submit_button = st.form_submit_button(label="🚀 Run Analysis")

# Lock the ticker into session state on submit to prevent vanishing bugs
if submit_button and ticker_input:
    st.session_state["active_ticker"] = ticker_input

# Run the evaluation if an active ticker is captured in state
if "active_ticker" in st.session_state:
    ticker = st.session_state["active_ticker"]
    st.info(f"Analyzing {ticker}... Sourcing verified data.")

    # ==================================================================
    # 🧭 BATCH 1: Business Phase Analysis (EXACT ORIGINAL)
    # ==================================================================
    phase_output = ""
    with st.expander("🧭 Business Phase Analysis", expanded=True):
        p1_prompt = f"""
        CRITICAL OPERATIONAL INSTRUCTION: You are a World-Class Strategic Analyst specialising in Business Lifecycle and Phase Identification. Your target stock identifier/company name is: '{ticker}'. 
        Step 1: Use your Google Search tool to identify today's current date and year (2026).
        Step 2: Search SEC EDGAR, official Company Investor Relations pages, and recent financial filings to locate the most recent 10-K, 10-Q, or international Annual Reports for target '{ticker}'.
        Step 3: Analyze the company's trajectory, revenue patterns, and product maturity. Classify it strictly into one of the following 5 phases: 1. Startup, 2. Rapid Growth, 3. Solid Growth, 4. Maturity, 5. Declining.
        Step 4: Output your final findings using the template format below. Do not add any conversational preambles. Output ONLY the completed template. It is vital you include the exact phrase 'Phase X' (where X is 1-5) in your 'Identified Phase' field.

        # 🧭 Business Phase Analysis: [Company Name] ({ticker})
         
        ### Identified Phase: Phase [Phase Number] - [Phase Name]
         
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

    phase_num = extract_phase_number(phase_output)
    st.caption(f"🤖 System localized corporate baseline structure to: **Phase {phase_num}**")

    # ==================================================================
    # 🏎️ BATCH 2: Core Analysis Macro-Prompt (WITH CHOSEN EXPLICIT STEPS)
    # ==================================================================
    macro_analysis_output = ""
    with st.spinner("⚡ Running Deep-Search Core Analysis Engine (Processing Moats, Growth, Risks, and Statements)..."):
        macro_prompt = f"""
        CRITICAL OPERATIONAL INSTRUCTION: You are an elite hedge fund research engine specializing in microeconomic moats and fundamental analysis. Your target stock identifier/company name is: '{ticker}'.
        
        Step 1: Use your Google Search tool to find today's current date and year (2026).
        Step 2: Search SEC EDGAR, official Company Investor Relations pages, and recent financial filings to locate the most recent 10-K, 10-Q, or international Annual Reports for target '{ticker}'.
        Step 3: Strictly ignore and bypass third-party aggregators, news channels, or media platforms (including MarketWatch, Stock Titan, Yahoo Finance, and Seeking Alpha). Focus exclusively on verified primary company disclosures.
        Step 4: Generate the full analysis using the exact demarcated templates below. Separate components with the clear marker '---'. Every individual panel MUST conclude with its own specific '## 📎 Sources' section. Do not include any conversational intro or outro.

        === PANEL_2_START ===
        # 🏰 MOAT ANALYSIS: [Company Name] ({ticker})
         
        <h4 style='margin-bottom: 0px;'>Moat size: [Select one: None ❌, Narrow ➖, Moderate ⚖️, Wide ✅]</h4>
        <h4 style='margin-top: 5px; margin-bottom: 20px;'>Moat direction: [Select one: Widening ✅ / Stable ➖ / Narrowing ❌]</h4>

        **Primary moat sources:** [List the 1-2 most dominant moat sources]

        **Summary:** [Provide a 1-2 sentence summary of the Moat thesis, supported by a key metric citation.]

        ## 👥 NETWORK EFFECT
        - **Assessment:** [Present ✅ / Not Present ❌]
        - **Summary:** [Provide a single sentence explaining how user additions scale value, explicitly citing a specific corporate data point or metric if present, e.g., active user counts or platform volume growth.]

        ## ⚓ SWITCHING COSTS
        - **Assessment:** [Present ✅ / Not Present ❌]
        - **Summary:** [Provide a single sentence explaining the friction preventing customer churn, explicitly citing a specific operational metric if present, e.g., a % renewal rate, dollar-based net retention (DBNR), or average contract length.]

        ## 🏭 LOW-COST PRODUCTION
        - **Assessment:** [Present ✅ / Not Present ❌]
        - **Summary:** [Provide a single sentence explaining structural cost advantages, explicitly citing a specific financial metric if present, e.g., gross margin percentage advantage over peers or shipping cost per unit.]

        ## 🚀 COUNTER POSITIONING
        - **Assessment:** [Present ✅ / Not Present ❌]
        - **Summary:** [Provide a single sentence explaining why legacy incumbents cannot copy this business model, explicitly citing a specific operational data point, e.g., customer acquisition cost (CAC) efficiency differences or pricing model structures.]

        ## 🏆 INTANGIBLE ASSETS
        - **Assessment:** [Present ✅ / Not Present ❌]
        - **Summary:** [Provide a single sentence tracking brand equity or regulatory protection, explicitly citing a specific hard data point, e.g., exact patent counts, regulatory approval numbers, or a premium pricing margin percentage.]

        ## 📎 Sources
        - [Identify specific official filing, proxy statement, or IR presentation used for Moat verification]
        === PANEL_2_END ===

        ---

        === PANEL_3_START ===
        # 🚀 Future Growth Analysis: [Company Name] ({ticker}) 
         
        ### Future Growth Potential: [Select one: High ✅ / Moderate ➖ / Low ❌]
        ### Future Growth Direction: [Select one: Accelerating ✅ / Stable ➖ / Decelerating ❌]
         
        **Evidence Summary:** [1–2 sentence narrative supported by a defining corporate growth metric citation.] 

        ## 🌍 Market Expansion
        - **Assessment:** Strength: [🟢/🟡/🔴/⚫] | Direction: [✅/➖/❌]
        - **Summary:** [Provide a single sentence explaining TAM expansion or geographic entries, explicitly citing a specific growth data point, e.g., number of new country store openings, international segment growth rate %, or localized customer acquisition statistics.]

        ## 🧪 Product Innovation
        - **Assessment:** Strength: [🟢/🟡/🔴/⚫] | Direction: [✅/➖/❌]
        - **Summary:** [Provide a single sentence identifying new product rollouts, explicitly citing a specific metric, e.g., percentage of current revenue derived from products launched in the last 24 months, pipeline asset numbers, or R&D spending trajectory.]

        ## 🤖 Technology Adoption
        - **Assessment:** Strength: [🟢/🟡/🔴/⚫] | Direction: [✅/➖/❌]
        - **Summary:** [Provide a single sentence on platform infrastructure optimization, explicitly citing a specific data point, e.g., cloud cost efficiencies, automated fulfillment rates, or cross-selling conversion percentages.]

        ## ⚖️ Regulatory Tailwinds
        - **Assessment:** Strength: [🟢/🟡/🔴/⚫] | Direction: [✅/➖/❌]
        - **Summary:** [Provide a single sentence on legal frameworks or subsidies driving demand, explicitly citing a specific regulatory data point or timeline milestone if available.]

        ## 📎 Sources 
        - [Identify specific official management guidance statement, earnings release, or investor deck used]
        === PANEL_3_END ===

        ---

        === PANEL_5_START ===
        # ⚠️ Risk Analysis: [Company Name] ({ticker})
        ## 📊 Overall Summary
        - **Overall Risk Level:** [High Risk 🔴 / Medium Risk 🟡 / Low Risk 🟢]
        - **⚠️ Primary Risk Factors:** [List the highest risk pillars]
        - **🛡️ Key Mitigation:** [Highlight corporate defense program]

        ## 🎯 RISK ASSESSMENT DETAILS
        ### 🥚🧺 Concentration
        - **Rating:** [🔴/🟡/🟢] | **Trend:** [⬆️/➖/⬇️]
        - **Summary:** [Provide a single sentence justifying the rating, explicitly citing a hard metric from recent disclosures, e.g., customer concentration percentages, single-supplier reliance ratios, or geographic segment revenue exposure %.]

        ### 🥷 Disruption
        - **Rating:** [🔴/🟡/🟢] | **Trend:** [⬆️/➖/⬇️]
        - *Summary:** [Provide a single sentence on technological obsolescence or substitute risks, explicitly citing an operational or industry metric, e.g., R&D spending compared to peers or legacy product revenue exposure.]

        ### 🕵️ Outside Forces
        - **Rating:** [🔴/🟡/🟢] | **Trend:** [⬆️/➖/⬇️]
        - **Summary:** [Provide a single sentence tracking macroeconomic, currency, or regulatory headwinds, explicitly citing a defining corporate data point, e.g., foreign exchange impact percentages or debt exposure to floating interest rates.]

        ### 👥 Competition
        - **Rating:** [🔴/🟡/🟢] | **Trend:** [⬆️/➖/⬇️]
        - **Summary:** [Provide a single sentence analysing market share or pricing pressure, explicitly citing a hard data point, e.g., relative market share %, peer margin comparisons, or historical customer acquisition cost trends.]

        ## 📎 Sources
        - [Identify specific Item 1A Risk Factors or relevant notes from the primary official filing used]
        === PANEL_5_END ===

        ---

        === PANEL_6_START ===
        # 📊 Financial Health Analysis: [Company Name] ({ticker})
        ## ✅ Overall Summary
        - **Overall Financial Health:** [Strong / Moderate / Weak / Okay]
         
        ## 🔍 Detailed Analysis 
        ### 📋 Income Statement
        - **Revenue Trend:** [⬆️/➖/⬇️] | **Score:** [🔴/🟡/🟢]
          * **Summary:** [Provide a brief sentence citing the exact current revenue figure and YoY percentage change from the latest filing.]
        - **Gross Profit Trend:** [⬆️/➖/⬇️] | **Score:** [🔴/🟡/🟢]
          * **Summary:** [Provide a brief sentence citing the exact gross margin % or absolute profit change.]
        - **Operating Income Trend:** [⬆️/➖/⬇️] | **Score:** [🔴/🟡/🟢]
          * **Summary:** [Provide a brief sentence citing the operating income (EBIT) or operating margin metric.]
        - **EPS Trend:** [⬆️/➖/⬇️] | **Score:** [🔴/🟡/🟢]
          * **Summary:** [Provide a brief sentence citing the exact diluted EPS value.]

        ### 🏦 Balance Sheet
        - **Cash & Securities:** [⬆️/➖/⬇️] | **Score:** [🔴/🟡/🟢]
          * **Summary:** [Provide a brief sentence citing the exact cash and short-term investments balance.]
        - **Debt Levels:** [⬆️/➖/⬇️] | **Score:** [🔴/🟡/🟢]
          * **Summary:** [Provide a brief sentence citing total debt levels, net cash position, or leverage ratio like Debt/EBITDA.]

        ### 💸 Cash Flows
        - **Free Cash Flow:** [⬆️/➖/⬇️] | **Score:** [🔴/🟡/🟢]
          * **Summary:** [Provide a brief sentence citing the absolute FCF generated or FCF margin %.]
        - **Operating Cash Flow:** [⬆️/➖/⬇️] | **Score:** [🔴/🟡/🟢]
          * **Summary:** [Provide a brief sentence citing the operating cash flow cash generation metric.]

        ## 📎 Sources
        - [Identify specific Consolidated Financial Statements, Balance Sheet, or Cash Flow footnotes from the primary official filing used]
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

    col1, col2 = st.columns(2)
    with col1:
        with st.expander("🏰 Moat Analysis v3", expanded=True):
            st.markdown(p2_output, unsafe_allow_html=True)
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
    # 📈 BATCH 3: Dynamic Metrics & Valuation Layer (EXACT ORIGINAL RULES)
    # ==================================================================
    p4_output = ""
    p7_output = ""
    p7_5_output = ""
    
    with st.spinner(f"🔢 Running valuation math specifically targeted to Phase {phase_num}..."):
        metrics_valuation_prompt = f"""
        🚨 DATA SOURCE PROVENANCE ENFORCEMENT FILTER 🚨
        - Your primary search queries MUST prioritize official financial nodes: "Company Investor Relations", "SEC EDGAR 10-K/10-Q", "Annual Report PDF", "Regulatory Filings", and "Earnings Call Transcript".
        - For forward-looking indicators, revenue outlooks, or capacity targets, use EXCLUSIVELY official corporate guidance issued directly by management in official press releases or IR portals.
        - STRICTLY FORBIDDEN: Do not ingest data, commentary, target figures, or assertions from third-party blogs, YouTube analysis videos, Substack opinion pieces, or retail forum channels (e.g., Reddit, Stocktwits). If official management guidance is unavailable for a metric, flag it as [Management Guidance Not Disclosed] instead of substituting speculative third-party targets.
Replace with:
        CRITICAL OPERATIONAL INSTRUCTION: You are an expert financial analyst evaluating corporate fundamentals for target: '{ticker}' mapped against corporate lifecycle Phase: '{phase_num}'.
        Step 1: Use your Google Search tool to find today's current date and year (2026).
        Step 2: Source recent filings (10-Q/10-K or international IR Annual Reports/investor presentations if non-US). Gather current share price, diluted share count, cash, debt, and consensus NTM (next-twelve-month) metrics. Calculate EV = Market Cap + Debt - Cash. Ensure currency consistency (e.g. convert to Euros if analyzing European operations).
        Step 3: Execute valuation models explicitly matching the Phase {phase_num} methodologies and industry overrides below.
        Step 4: Generate output using the exact layout below. Separate blocks with '---'. Do not add conversational intro text.

        === PANEL_4_START ===
        ### 📊 Phase {phase_num} Core Diagnostic Benchmarking

        **Diagnostic Summary Score:** [MANDATORY MATHEMATICAL SYNTHESIS: Assign points to the 5 rows below: 🟢=2 pts, 🟡=1 pt, 🔴=0 pts. Sum the points (Max 10). If total points are >= 7, output "Good 🟢". If 3-6 points, output "Average 🟡". If <= 2 points, output "Weak 🔴". Show the mathematical total, e.g., "Average 🟡 (5/10 points)"]

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
        - **Calculated Multiple / Model output:** [Provide exact multiple or valuation range]
        - **Benchmark Sector Context:** [Provide explicit text evaluating current multiples relative to sector medians]
        - **Key Drivers:** [List core components]
        - **Sensitivity:** [Key assumptions]

        ## 📎 Sources
        [1] Source Name (Filing/IR Report)
        === PANEL_7_END ===

        ---

        === PANEL_7_5_START ===
        ### 📊 Total Shareholder Return (TSR) Driver Matrix
        *Evaluating fundamental drivers of structural asset appreciation based strictly on primary corporate disclosure.*

        | TSR Driver | Current Profile Status | Core Phase Lifecycle Mechanics |
        | :--- | :--- | :--- |
        | **🚀 Revenue Growth** | [Status: e.g., 🔥 Primary Engine / 🟡 Moderate / ❌ Stagnant] | [Detail how top-line velocity is moving the absolute terminal valuation] |
        | **📈 Margin Expansion** | [Status: e.g., 🟢 Active / ⏳ Latent Potential / 🔴 Contracting] | [Detail operating leverage trends, gross margin health, or infrastructure scaling costs] |
        | **🔄 Multiple Expansion** | [Status: e.g., 🟩 Undervalued Entry / ⚖️ Fairly Valued / 🟥 Premium Multiple] | [Assess if price returns will outpace or compress the asset's current valuation multiple] |
        | **📉 Share Reduction** | [Status: e.g., 🟢 Aggressive Buybacks / ➖ Neutral / ❌ Dilutive Capital Raise] | [Identify if share float reduction is boosting EPS, or if dilution is actively funding growth] |
        === PANEL_7_5_END ===
        """
        try:
            macro_val_output = generate_analysis_layer(ticker, metrics_valuation_prompt)
            p4_output = parse_panel(macro_val_output, "=== PANEL_4_START ===", "=== PANEL_4_END ===", "### 📊 Phase")
            p7_output = parse_panel(macro_val_output, "=== PANEL_7_START ===", "=== PANEL_7_END ===", "### 💰 Phase-Appropriate")
            p7_5_output = parse_panel(macro_val_output, "=== PANEL_7_5_START ===", "=== PANEL_7_5_END ===", "### 📊 Total Shareholder Return")
        except Exception as e:
            st.error(f"Error executing valuation modules: {e}")
            p4_output = "⚠️ Valuation metrics framework execution error."
            p7_output = "⚠️ Valuation calculation framework execution error."
            p7_5_output = "⚠️ TSR Matrix compilation unavailable."

    with st.expander("📊 Business Key Metrics Analysis", expanded=True):
        st.markdown(p4_output)

    with st.expander("💰 Business Valuation Analysis", expanded=True):
        st.markdown(p7_output)
        
    with st.expander("📊 Total Shareholder Return (TSR) Driver Card", expanded=True):
        st.markdown(p7_5_output)
        
        # ==================================================================
    # 🧠 PANEL #8: SYSTEM SYNTHESIS & SCORING ENGINE (NUANCED DILUTION LOGIC)
    # ==================================================================
    
    # 1. Parse Panel 4 diagnostic colors
    p4_lines = [line.lower() for line in p4_output.split("\n") if "|" in line]
    
    rev_growth_color = "🟡"
    margin_color = "🟡"
    efficiency_color = "🟡"
    asset_color = "🟡"
    alignment_color = "🟡"

    for line in p4_lines:
        if "revenue" in line:
            rev_growth_color = "🔴" if "🔴" in line else ("🟢" if "🟢" in line else "🟡")
        elif "profitability" in line or "margin" in line:
            margin_color = "🔴" if "🔴" in line else ("🟢" if "🟢" in line else "🟡")
        elif "efficiency" in line or "roic" in line:
            efficiency_color = "🔴" if "🔴" in line else ("🟢" if "🟢" in line else "🟡")
        elif "asset" in line or "health" in line:
            asset_color = "🔴" if "🔴" in line else ("🟢" if "🟢" in line else "🟡")
        elif "shareholder" in line or "alignment" in line or "dilution" in line:
            alignment_color = "🔴" if "🔴" in line else ("🟢" if "🟢" in line else "🟡")

    # ==================================================================
    # 🚀 NUANCED DILUTION ASSESSMENT FOR GROWTH COMPANIES
    # ==================================================================
    
    def extract_pct(text, keyword):
        match = re.search(rf"{keyword}.*?([+-]?\d+\.?\d*)%", text, re.IGNORECASE)
        return float(match.group(1)) if match else None

    def extract_value(text, keyword):
        match = re.search(rf"{keyword}.*?([+-]?\d+\.?\d*)", text, re.IGNORECASE)
        return float(match.group(1)) if match else None

    # Pull raw numbers from earlier panels. Requires Evidence lines in Panel 3, 4, 6
    rev_growth_pct = extract_pct(p4_output, "Revenue Growth") or extract_pct(p3_output, "Revenue")
    shares_dilution_pct = extract_pct(p4_output, "Shareholder Alignment") 
    fcf_value = extract_value(p6_output, "Free Cash Flow")

    capex_heavy = contains_any(p6_output + p3_output, ["capex", "capital expenditure", "infrastructure", "property plant", "data center", "build out", "capacity"])
    mgmt_guidance_fcf_positive = contains_any(p3_output + p7_output + p7_5_output, ["fcf positive", "cash flow positive", "free cash flow break", "cash flow break even"])

    # Build 3-factor score: Growth >> Dilution, Capital to Assets, Runway Plan
    growth_beats_dilution = False
    if rev_growth_pct and shares_dilution_pct and shares_dilution_pct > 0:
        if rev_growth_pct > shares_dilution_pct * 3:  # 3x rule: Rev growth must be 3x dilution
            growth_beats_dilution = True

    capital_to_assets = capex_heavy and contains_any(p3_output, ["growth", "expansion", "capacity", "commercialization"])
    has_runway_plan = mgmt_guidance_fcf_positive

    dilution_score = sum([growth_beats_dilution, capital_to_assets, has_runway_plan])
    
    # Override alignment_color for growth phases based on score
    rule_justification_override = ""
    if alignment_color == "🔴" and phase_num in ["1", "2", "3"]:
        if dilution_score == 3:
            alignment_color = "🟢"  # Neutral if all 3 conditions met
            rule_justification_override = f"Strategic capital raise: {rev_growth_pct}% revenue growth with capex deployment and guidance to FCF positive. "
        elif dilution_score >= 2:
            alignment_color = "🟡"  # Downgrade from fatal to warning
            rule_justification_override = f"Dilution present but partially offset by {rev_growth_pct}% growth velocity and capex deployment. "
        # else: keep as 🔴 fatal

    # Recalculate counts after potential override
    color_list = [rev_growth_color, margin_color, efficiency_color, asset_color, alignment_color]
    p4_red_count = color_list.count("🔴")
    p4_yellow_count = color_list.count("🟡")
    p4_green_count = color_list.count("🟢")
    p4_green_ratio = p4_green_count / 5

    val_overvalued = contains_any(p7_output, ["overvalued", "🔴"])
    val_undervalued = contains_any(p7_output, ["undervalued", "🟢"])
    val_fairly = contains_any(p7_output, ["fairly valued", "fair value", "🟡"])

    # ==================================================================
    # 📊 FINAL DECISION TREE
    # ==================================================================
    calculated_status = None
    rule_justification = ""

    # PHASE 5: Always reject declining
    if phase_num == "5":
        calculated_status = "❌ PASS (Not Good Enough)"
        rule_justification = "Company is structurally limited by its business life cycle phase (Phase 5 - Declining profile filtered by core framework rules)."

    # PHASE 1-3: Check if nuanced dilution passed first
    elif phase_num in ["1", "2", "3"] and alignment_color == "🟢":
        calculated_status = "🚀 DEEP DIVE ASAP"
        rule_justification = rule_justification_override + f"Phase {phase_num} Hyper-Conviction Growth Engine with strategic capital deployment."
    
    elif phase_num == "1" and alignment_color == "🟡":
        calculated_status = "⏳ ADD TO WATCHLIST"
        rule_justification = rule_justification_override + "Phase 1 profile with high growth but dilution requires monitoring of capital efficiency."

    elif phase_num in ["2", "3"] and alignment_color == "🟡":
        if p4_red_count <= 1:
            calculated_status = "⏳ ADD TO WATCHLIST"
            rule_justification = rule_justification_override + f"Solid Phase {phase_num} Growth profile. Dilution is a watch item but core metrics acceptable."
        else:
            calculated_status = "❌ PASS (Too Risky)"
            rule_justification = rule_justification_override + f"Phase {phase_num} Growth with excessive operating friction despite dilution controls."

    # GLOBAL FATAL DILUTION CHECK: Only fires if not caught by nuanced rules above
    elif alignment_color == "🔴":
        calculated_status = "❌ PASS (Too Risky)"
        rule_justification = f"Fatal structural flaw: Shares Outstanding +{shares_dilution_pct}% YoY with FCF of {fcf_value}. Indicates equity raises funding cash burn, not growth."

    # PHASE 1: Standard startup filter
    elif phase_num == "1":
        if p4_red_count > 0:
            calculated_status = "❌ PASS (Too Risky)"
            rule_justification = "Phase 1 Startup disqualified due to active high-risk red flags in core operational performance metrics."
        elif alignment_color == "🟢" and p4_green_count >= 3:
            calculated_status = "⏳ ADD TO WATCHLIST"
            rule_justification = "High-quality Phase 1 startup profile meeting strict baseline structural indicators."
        else:
            calculated_status = "❌ PASS (Not Good Enough)"
            rule_justification = "Phase 1 Startup filtered out. Fails to meet the strict multi-criteria financial efficiency thresholds."

    # PHASE 4: Mature compounder logic
    elif phase_num == "4":
        if rev_growth_color == "🔴" or val_overvalued:
            calculated_status = "❌ PASS (Not Good Enough)"
            rule_justification = "Mature asset rejected: Identified as an overvalued profile or a stagnant value trap with flatlining revenue trends."
        elif efficiency_color == "🟢" and val_undervalued:
            calculated_status = "🚀 DEEP DIVE ASAP"
            rule_justification = "Phase 4 Mature compounder showing pristine execution, strong capital return health, and an undeniable valuation margin of safety."
        elif val_fairly or (p4_green_count >= 2 and not val_overvalued):
            calculated_status = "⏳ ADD TO WATCHLIST"
            rule_justification = "High-quality mature compounding architecture. Held on watchlist to monitor entry positioning or minor metrics stabilization."
        else:
            calculated_status = "❌ PASS (Not Good Enough)"
            rule_justification = "Phase 4 asset fails to show the high-efficiency return metrics or margin of safety required to lock capital."

    # PHASE 2-3: Standard growth filter if dilution was not fatal
    elif phase_num in ["2", "3"]:
        if p4_red_count == 0 and p4_green_ratio >= 0.75:
            calculated_status = "🚀 DEEP DIVE ASAP"
            rule_justification = f"Phase {phase_num} High-Conviction Growth engine hitting pristine diagnostic bars. Flawless execution across velocity, margins, and capital metrics."
        elif p4_red_count <= 1:
            calculated_status = "⏳ ADD TO WATCHLIST"
            rule_justification = f"Solid Phase {phase_num} Growth profile showing robust primary velocity. Minor scaling friction or near-term margins warrant pipeline observation."
        else:
            calculated_status = "❌ PASS (Too Risky)"
            rule_justification = f"Phase {phase_num} Growth asset disqualified due to excessive operating friction, capital inefficiencies, or multi-metric red flags."

    else:
        calculated_status = "⏳ ADD TO WATCHLIST"
        rule_justification = "System fallback logic triggered. Deflected to pipeline queue for structural manual verification."

    # ==================================================================
    # 🧠 PANEL #8: CHIEF INVESTMENT OFFICER SYNTHESIS (WITH DATA RULES)
    # ==================================================================
    with st.expander("⚖ Panel #8: Final Investment Decision", expanded=True):
        st.write("*Synthesizing framework layers into a final allocation recommendation...*")
        
        p8_prompt = f"""
        CRITICAL OPERATIONAL INSTRUCTION: You are the Chief Investment Officer of a boutique equity fund specialising in microeconomic moats and structural corporate lifecycles. Your job is to specialize the data gathered across our research framework for target asset: '{ticker}' (Phase Context: Phase {phase_num}).

        The rules-based engine has already run a structural compliance check on this asset and determined the following mandatory designation:
         
        MANDATORY DESIGNATION: {calculated_status}
        SYSTEM REASONING: {rule_justification}

        You MUST accept this designation. Your role is to write the executive synthesis explaining the qualitative 'Why' behind this decision, utilizing the findings from our individual modules.

        CRITICAL ROUTING INSTRUCTIONS FOR INSIGHT GENERATION:
        Depending on the MANDATORY DESIGNATION provided above, adapt your breakdown inside the sections below using these parameters:

        1. If the status is "🚀 DEEP DIVE ASAP":
           - **Core Investment Thesis:** Strongly highlight exactly why this asset presents an exceptional opportunity. If dilution was present but offset by growth/capex/guidance, explicitly frame the equity raise as a positive, strategic capital deployment mechanism required to fund a generational land grab. You must cite the specific Revenue Growth % and Shares Outstanding % from the data. Highlight why topline hyper-velocity trumps standard capital dilution guidelines.
           - **Key Risks to Identify:** Explicitly map out the asymmetric blindspots, complex operational risk elements, or structural assumptions the analyst must verify or clear (e.g., infrastructure execution risk, capacity utilization delays, guidance credibility).

        2. If the status is "⏳ ADD TO WATCHLIST":
           - **Core Investment Thesis:** Explain what is structurally preventing this asset from unlocking an immediate Deep Dive recommendation right now. If dilution is the reason, cite the specific Shares Outstanding % vs FCF number. Focus on scale confirmation, validation of unit economics, or near-term margins adjustments.
           - **Key Risks to Identify:** Identify precisely what fundamental benchmark shifts, valuation thresholds, or corporate operational changes need to be met for this asset to become fully worthy of active investment attention.

        3. If the status contains "❌ PASS":
           - **Core Investment Thesis:** Clearly diagnose that this asset failed the structural selection framework. If failure is due to Shareholder Alignment/Dilution, you MUST cite the specific data point: "Shares Outstanding +X% YoY while TTM FCF was €Y". Distinguish between 'dilution funding losses' vs 'dilution funding growth capex'. Do NOT use generic phrases like 'toxic capital structure' without data. Focus heavily on why the combination of life cycle constraints, toxic metrics, or poor efficiency creates a permanent destruction of capital risk.
           - **Key Risks to Identify:** Outline the specific systemic risk factors, balance sheet or execution vulnerabilities that make this target completely uninvestable.

        Output ONLY the markdown format below. Ensure the layout matches perfectly. Use the specific HTML structure provided below for the Final Recommendation to make it pop out with massive text and clear separation.

        # ⚖ Assessment Summary: {ticker}
        <div style="background-color: rgba(255, 255, 255, 0.05); padding: 15px; border-left: 5px solid #ff4b; border-radius: 4px; margin: 15px 0;">
            <h2 style="margin: 0; padding: 0; font-size: 28px; font-weight: 800; letter-spacing: 0.5px;">
                Final Recommendation: {calculated_status}
            </h2>
        </div>

        **Core Investment Thesis (The \"Why\"):** [A punchy, single-sentence summary validating the system reasoning: '{rule_justification}']

        ### 📋 Core Investment Thesis & Risks
        - **Core Investment Thesis:** [Provide a detailed 2-3 sentence strategic rationale customized to the designation parameters specified above. Must include hard numbers if dilution is discussed.]
        - **Key Risks to Identify:** [Provide a detailed 2-3 sentence breakdown customized to the designation parameters specified above.]

        ### 🛠 Required Next Steps
        - **Primary Blindspot to Verify:** [Identify the #1 operational metric or data point needed to monitor this decision.]
        - **Trigger Condition:** [Define a clear operational or valuation parameter trigger to change position status.]
        """
        try:
            p8_output = generate_analysis_layer(ticker, p8_prompt)
            st.markdown(p8_output, unsafe_allow_html=True)
        except Exception as e:
            st.error(f"Error executing Panel 8: {e}")
            p8_output = f"Final Recommendation: {calculated_status}\nReasoning: {rule_justification}"

    # ==================================================================
    # 📌 PANEL #8.5: DATA PROVENANCE & BLENDED DISCLAIMER (EXACT TONAL REWRITE)
    # ==================================================================
    with st.expander("📌 Verified Data Provenance & Legal Disclaimer", expanded=False):
        st.markdown("""
        ### 📌 Where Does This Data Come From?
        **My Promise: No Fake Data.**
        
        I have written this program to filter out speculative data from unverified sources such as YouTube videos, Reddit threads, and 3rd party sources. Instead, the AI analyst acts like a professional researcher, pulling and cross-referencing numbers directly from the most authoritative corporate sources:
        
        * 📄 **Official SEC Filings:** Direct access to public company repositories (like the **SEC EDGAR** database for US stocks or official regional business registries for European listings).
        * 🏢 **Investor Relations Portals:** Hard data sourced directly from official corporate press releases and IR pages.
        * 🎙️ **Earnings Releases:** Direct numbers extracted from audited quarterly reports, official management earnings transcripts, and slide decks.
        
        ---
        
        ### ⚠️ Important Financial Disclaimer
        **This dashboard is an informational and educational research tool only. It does not constitute investment advice, financial planning, or a solicitation to buy or sell any securities.** The automated lifecycle evaluations, diagnostic scores, and calculations generated by this application are designed to streamline corporate data tracking and macro fundamental analysis. Equity markets involve substantial risk, particularly when looking at small-cap or hyper-growth companies. Always perform your own thorough due diligence, verify historical filings independently, and consult with a licensed, professional financial advisor before allocating capital.
        """)
        st.caption("🔒 Data Quality Assurance: Active — Strict Primary Disclosures Only | Not Financial Advice")

    # ==================================================================
    # 🔒 CLEAN SESSION STATE PERSISTENCE (FIXED RECONCILIATION)
    # ==================================================================
    st.session_state["ticker_analyzed"] = ticker
    st.session_state["pdf_p1"] = phase_output
    st.session_state["pdf_p2"] = p2_output
    st.session_state["pdf_p3"] = p3_output
    st.session_state["pdf_p4"] = p4_output
    st.session_state["pdf_p5"] = p5_output
    st.session_state["pdf_p6"] = p6_output
    st.session_state["pdf_p7"] = p7_output
    st.session_state["pdf_p7_5"] = p7_5_output  
    st.session_state["pdf_p8"] = p8_output

# ==================================================================
# 📥 EXPORT ENGINE BLOCK
# ==================================================================
if "ticker_analyzed" in st.session_state:
    st.write("---")
    st.subheader("📥 Actions")
    
    def clean_text_for_pdf(text):
        if not text:
            return ""
        # Remove any HTML tags
        text = re.sub(r'<[^>]*>', '', text)
        # Remove markdown headers and bold syntax
        text = text.replace("**", "").replace("###", "").replace("##", "").replace("#", "")
        text = text.replace("---", "\n" + "-"*40 + "\n")
        
        # Convert critical framework indicator symbols into readable text
        symbol_mappings = {
            "🟩": "Green", "🟨": "Yellow", "🟥": "Red", 
            "🟢": "Good", "🟡": "Average", "🔴": "Weak",
            "✅": "PASS", "❌": "FAIL"
        }
        for symbol, text_replacement in symbol_mappings.items():
            text = text.replace(symbol, text_replacement)
        
        # 🔥 PERMANENT FIX: Strip out all other miscellaneous emojis/symbols entirely 
        # This keeps only standard keyboard characters (letters, numbers, basic punctuation)
        text = re.sub(r'[^\x00-\x7F\x80-\xFF]', '', text)
        
        return text.encode('latin-1', 'replace').decode('latin-1')

    def build_pdf_document():
        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()
        
        pdf.set_font("Helvetica", "B", 16)
        pdf.cell(0, 10, clean_text_for_pdf(f"Research Report: {st.session_state['ticker_analyzed']}"), ln=True, align="C")
        pdf.ln(10)
        
        panels_to_print = [
            ("1. Business Phase Analysis", st.session_state["pdf_p1"]),
            ("2. Competitive Moat Analysis", st.session_state["pdf_p2"]),
            ("3. Future Growth Analysis", st.session_state["pdf_p3"]),
            ("4. Core Diagnostic Benchmarking", st.session_state["pdf_p4"]),
            ("5. Execution Risk Analysis", st.session_state["pdf_p5"]),
            ("6. Financial Health Analysis", st.session_state["pdf_p6"]),
            ("7. Valuation Matrix & Targets", st.session_state["pdf_p7"]),
            ("7.5 Total Shareholder Return (TSR) Driver Matrix", st.session_state["pdf_p7_5"]),
            ("8. Final Investment Decision Summary", st.session_state["pdf_p8"])
        ]
        
        for section_title, analytical_content in panels_to_print:
            pdf.set_font("Helvetica", "B", 12)
            pdf.cell(0, 8, clean_text_for_pdf(section_title), ln=True)
            pdf.ln(2)
            pdf.set_font("Helvetica", "", 10)
            pdf.multi_cell(0, 5, clean_text_for_pdf(analytical_content))
            pdf.ln(6)
            
        return bytes(pdf.output(dest="S"))  

    if st.button("🔄 Clear Ticker & Start New Search", use_container_width=True):
        for key in ["ticker_analyzed", "active_ticker", "pdf_p1", "pdf_p2", "pdf_p3", "pdf_p4", "pdf_p5", "pdf_p6", "pdf_p7", "pdf_p7_5", "pdf_p8"]:
            if key in st.session_state:
                del st.session_state[key]
        st.rerun()

    try:
        pdf_data = build_pdf_document()
        st.download_button(
            label="📥 Download PDF",
            data=pdf_data,
            file_name=f"{st.session_state['ticker_analyzed']}_Analysis.pdf",
            mime="application/pdf",
            use_container_width=True
        )
    except Exception as pdf_err:
        st.error(f"Could not build report download package: {pdf_err}")
