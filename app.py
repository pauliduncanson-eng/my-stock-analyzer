
# 1. Page Configuration & Styling
st.set_page_config(page_title="European Hidden Gems Analyzer", layout="wide")
st.title("📊 European Hidden Gems Research Dashboard")
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

# Helper function to extract the single digit phase number from the model's text output
def extract_phase_number(text):
    if not text:
        return "3"
    match = re.search(r'\b(Phase\s*([1-5])|([1-5])\b)', text, re.IGNORECASE)
    if match:
        return match.group(2) if match.group(2) else match.group(3)
    return "3"

# Robust Smart Parsing Engine to capture data under any formatting variance
def parse_panel(text, start_tag, end_tag, fallback_header=None):
    if not text or not isinstance(text, str):
        return "⚠️ *Analysis data temporarily unavailable. Please rerun.*"
# ==================================================================
# 🔒 PASSWORD PROTECTION GATEWAY
# ==================================================================
def check_password():
    """Returns True if the user has entered the correct password."""
    # Initialize session state if it doesn't exist
    if "password_correct" not in st.session_state:
        st.session_state.password_correct = False

    # If already unlocked, skip the login screen
    if st.session_state.password_correct:
        return True

    # Render the clean login screen interface
    st.markdown("## 🔒 European Hidden Gems Research Portal")
    st.write("This proprietary dashboard is reserved for community members.")

    clean_start = start_tag.replace("=", "").strip()
    clean_end = end_tag.replace("=", "").strip()
    user_password = st.text_input("Enter your access password:", type="password")

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
    if st.button("Unlock Dashboard"):
        # Matches your exact requested password (case-sensitive)
        if user_password == "GEMS":
            st.session_state.password_correct = True
            st.success("🔓 Access Granted!")
            time.sleep(0.5)  # Brief pause to let the success message register
            st.rerun()
        elif user_password == "":
            st.warning("Please enter a password.")
        else:
            st.error("❌ Incorrect password. Please try again.")

    if "PANEL_4" in start_tag or "PANEL_2" in start_tag:
        split_point = len(text) // 2
        return text[:split_point].strip() + "\n\n*(Note: Data recovered via structural backup layout parser)*"
    elif "PANEL_7" in start_tag or "PANEL_3" in start_tag:
        split_point = len(text) // 2
        return text[split_point:].strip() + "\n\n*(Note: Data recovered via structural backup layout parser)*"

    return text

# Helper function to scan panels for loose keyword groupings/synonyms
def contains_any(text, keywords):
    if not text:
        return False
    text_lower = text.lower()
    return any(kw in text_lower for kw in keywords)

# 4. User Input Interface
with st.form(key="research_panel_form"):
    ticker = st.text_input(
        "Add ticker to run stock analysis:", 
        placeholder="e.g., Robot S.A. (EPA:ALROB)"
    )
    
    st.markdown(
        "Enter both the company name and the ticker symbol "
        "according to Google Finance (e.g., *Robot S.A. EPA:ALROB* or *Archos SA EPA:ALJAC*)."
    )
    
    submit_button = st.form_submit_button(label="Run the analysis")
    return False

# 5. Run Analysis Framework Upon Submission
if submit_button and ticker:
    st.info(f"Analyzing {ticker}... Pulling primary filings, establishing lifecycle phase, and processing framework panels.")
# Execute the password gate. Only run the framework if check_password() returns True.
if check_password():

# ==================================================================
    # 🧭 BATCH 1: Business Phase Analysis
    # 📊 CORE APP FRAMEWORK (UNLOCKED)
# ==================================================================
    phase_output = ""
    with st.expander("🧭 Business Phase Analysis", expanded=True):
        st.write("*Fetching latest structural lifecycle positioning...*")
        p1_prompt = f"""
        CRITICAL OPERATIONAL INSTRUCTION: You are a World-Class Strategic Analyst specialising in Business Lifecycle and Phase Identification. Your target stock identifier/company name is: '{ticker}'. 
        Step 1: Use your Google Search tool to identify today's current date and year (2026).
        Step 2: Search SEC EDGAR, official Company Investor Relations pages, and recent financial filings to locate the most recent 10-K, 10-Q, or international Annual Reports for target '{ticker}'.
        Step 3: Analyze the company's trajectory, revenue patterns, and product maturity. Classify it strictly into one of the following 5 phases: 1. Startup, 2. Rapid Growth, 3. Solid Growth, 4. Maturity, 5. Declining.
        Step 4: Output your final findings using the template format below. Do not add any conversational preambles. Output ONLY the completed template. It is vital you include the exact phrase 'Phase X' (where X is 1-5) in your 'Identified Phase' field.

        # 🧭 Business Phase Analysis: [Company Name] ({ticker})
    st.title("📊 European Hidden Gems Research Dashboard")
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

        ### Identified Phase: Phase [Phase Number] - [Phase Name]
        models_to_try = ["gemini-2.5-flash", "gemini-2.5-pro"]
        max_retries = 3

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

    # Helper function to extract the single digit phase number from the model's text output
    def extract_phase_number(text):
        if not text:
            return "3"
        match = re.search(r'\b(Phase\s*([1-5])|([1-5])\b)', text, re.IGNORECASE)
        if match:
            return match.group(2) if match.group(2) else match.group(3)
        return "3"

    # ==================================================================
    # 🏎️ BATCH 2: Core Analysis Macro-Prompt
    # ==================================================================
    macro_analysis_output = ""
    with st.spinner("⚡ Running Deep-Search Core Analysis Engine (Processing Moats, Growth, Risks, and Statements)..."):
        macro_prompt = f"""
        CRITICAL OPERATIONAL INSTRUCTION: You are an elite hedge fund research engine. Perform a comprehensive analysis on target stock identifier/company name: '{ticker}'.
        Step 1: Use your Google Search tool to find today's current date/year (2026).
        Step 2: Source recent regulatory filings (SEC EDGAR, European company registries, or investor relations centers) and earnings call transcripts.
        Step 3: Generate the full analysis using the exact demarcated templates below. Separate components with the clear marker '---'. Do not include any conversational intro or outro.

        === PANEL_2_START ===
        # 🏰 MOAT ANALYSIS: [Company Name] ({ticker})
    # Robust Smart Parsing Engine to capture data under any formatting variance
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

    # Helper function to scan panels for loose keyword groupings/synonyms
    def contains_any(text, keywords):
        if not text:
            return False
        text_lower = text.lower()
        return any(kw in text_lower for kw in keywords)

    # 4. User Input Interface
    with st.form(key="research_panel_form"):
        ticker = st.text_input(
            "Add ticker to run stock analysis:", 
            placeholder="e.g., Robot S.A. (EPA:ALROB)"
        )

        <h4 style='margin-bottom: 0px;'>Moat size: [Select one: None ❌, Narrow ➖, Moderate ⚖️, Wide ✅]</h4>
        <h4 style='margin-top: 5px; margin-bottom: 20px;'>Moat direction: [Select one: Widening ✅ / Stable ➖ / Narrowing ❌]</h4>
        st.markdown(
            "Enter both the company name and the ticker symbol."
        )
        
        submit_button = st.form_submit_button(label="Run the analysis")

    # 5. Run Analysis Framework Upon Submission
    if submit_button and ticker:
        st.info(f"Analyzing {ticker}... Pulling primary filings, establishing lifecycle phase, and processing framework panels.")

        # ==================================================================
        # 🧭 BATCH 1: Business Phase Analysis
        # ==================================================================
        phase_output = ""
        with st.expander("🧭 Business Phase Analysis", expanded=True):
            st.write("*Fetching latest structural lifecycle positioning...*")
            p1_prompt = f"""
            CRITICAL OPERATIONAL INSTRUCTION: You are a World-Class Strategic Analyst specialising in Business Lifecycle and Phase Identification. Your target stock identifier/company name is: '{ticker}'. 
            Step 1: Use your Google Search tool to identify today's current date and year (2026).
            Step 2: Search SEC EDGAR, official Company Investor Relations pages, and recent financial filings to locate the most recent 10-K, 10-Q, or international Annual Reports for target '{ticker}'.
            Step 3: Analyze the company's trajectory, revenue patterns, and product maturity. Classify it strictly into one of the following 5 phases: 1. Startup, 2. Rapid Growth, 3. Solid Growth, 4. Maturity, 5. Declining.
            Step 4: Output your final findings using the template format below. Do not add any conversational preambles. Output ONLY the completed template. It is vital you include the exact phrase 'Phase X' (where X is 1-5) in your 'Identified Phase' field.

            # 🧭 Business Phase Analysis: [Company Name] ({ticker})
            
            ### Identified Phase: Phase [Phase Number] - [Phase Name]
            
            **Confidence Level:** [High / Medium / Low]

        **Primary moat sources:** [List the 1-2 most dominant moat sources]
            ### 📊 Phase Diagnostic Matrix
            - **Revenue Growth Profile:** [Describe current trajectory vs historical baseline]
            - **Profitability & Cash Flows:** [Identify status of Net Income, Operating Margins, and FCF generation]
            - **Capital Allocation Trends:** [Note major behaviors like heavy R&D investment, aggressive M&A, share buybacks, or dividend payouts]

        **Summary:** [Provide a 1-2 sentence summary of the Moat thesis, supported by a key metric citation.]
            ### 🔬 Phase Justification Narrative
            [Provide a clear, cohesive 2-3 sentence paragraph explaining precisely why the company fits into this specific lifecycle phase based on the financial evidence.]

        ## 👥 NETWORK EFFECT
        **Assessment:** [Present ✅ / Not Present ❌]
        ## ⚓ SWITCHING COSTS
        **Assessment:** [Present ✅ / Not Present ❌]
        ## 🏭 LOW-COST PRODUCTION
        **Assessment:** [Present ✅ / Not Present ❌]
        ## 🚀 COUNTER POSITIONING
        **Assessment:** [Present ✅ / Not Present ❌]
        ## 🏆 INTANGIBLE ASSETS
        **Assessment:** [Present ✅ / Not Present ❌]
        === PANEL_2_END ===
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
        # 🏎️ BATCH 2: Core Analysis Macro-Prompt
        # ==================================================================
        macro_analysis_output = ""
        with st.spinner("⚡ Running Deep-Search Core Analysis Engine (Processing Moats, Growth, Risks, and Statements)..."):
            macro_prompt = f"""
            CRITICAL OPERATIONAL INSTRUCTION: You are an elite hedge fund research engine. Perform a comprehensive analysis on target stock identifier/company name: '{ticker}'.
            Step 1: Use your Google Search tool to find today's current date/year (2026).
            Step 2: Source recent regulatory filings (SEC EDGAR, European company registries, or investor relations centers) and earnings call transcripts.
            Step 3: Generate the full analysis using the exact demarcated templates below. Separate components with the clear marker '---'. Do not include any conversational intro or outro.

            === PANEL_2_START ===
            # 🏰 MOAT ANALYSIS: [Company Name] ({ticker})
            
            <h4 style='margin-bottom: 0px;'>Moat size: [Select one: None ❌, Narrow ➖, Moderate ⚖️, Wide ✅]</h4>
            <h4 style='margin-top: 5px; margin-bottom: 20px;'>Moat direction: [Select one: Widening ✅ / Stable ➖ / Narrowing ❌]</h4>

        ---
            **Primary moat sources:** [List the 1-2 most dominant moat sources]

        === PANEL_3_START ===
        # 🚀 Future Growth Analysis: [Company Name] ({ticker}) 
        
        ### Future Growth Potential: [Select one: High ✅ / Moderate ➖ / Low ❌]
        ### Future Growth Direction: [Select one: Accelerating ✅ / Stable ➖ / Decelerating ❌]
        
        **Evidence Summary:** [1–2 sentence narrative supported by a defining corporate growth metric citation.] 

        ## 🌍 Market Expansion
        **Assessment:** Strength: [🟢/🟡/🔴/⚫] | Direction: [✅/➖/❌]
        ## 🧪 Product Innovation
        **Assessment:** Strength: [🟢/🟡/🔴/⚫] | Direction: [✅/➖/❌]
        ## 🤖 Technology Adoption
        **Assessment:** Strength: [🟢/🟡/🔴/⚫] | Direction: [✅/➖/❌]
        ## ⚖️ Regulatory Tailwinds
        **Assessment:** Strength: [🟢/🟡/🔴/⚫] | Direction: [✅/➖/❌]
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
        ### 🥷 Disruption
        - **Rating:** [🔴/🟡/🟢] | **Trend:** [⬆️/➖/⬇️]
        ### 🕵️ Outside Forces
        - **Rating:** [🔴/🟡/🟢] | **Trend:** [⬆️/➖/⬇️]
        ### 👥 Competition
        - **Rating:** [🔴/🟡/🟢] | **Trend:** [⬆️/➖/⬇️]
        === PANEL_5_END ===

        ---

        === PANEL_6_START ===
        # 📊 Financial Health Analysis: [Company Name] ({ticker})
        ## ✅ Overall Summary
        - **Overall Financial Health:** [Strong / Moderate / Weak / Okay]
        
        ## 🔍 Detailed Analysis 
        ### 📋 Income Statement
        - **Revenue Trend:** [⬆️/➖/⬇️] | **Score:** [🔴/🟡/🟢]
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
            **Summary:** [Provide a 1-2 sentence summary of the Moat thesis, supported by a key metric citation.]

    # ==================================================================
    # 📈 BATCH 3: Dynamic Metrics & Valuation Layer
    # ==================================================================
    p4_output = ""
    p7_output = ""
    with st.spinner(f"🔢 Running valuation math specifically targeted to Phase {phase_num}..."):
        metrics_valuation_prompt = f"""
        CRITICAL OPERATIONAL INSTRUCTION: You are an expert financial analyst evaluating corporate fundamentals for target: '{ticker}' mapped against corporate lifecycle Phase: '{phase_num}'.
        Step 1: Use your Google Search tool to find today's current date and year (2026).
        Step 2: Source recent filings (10-Q/10-K or international IR Annual Reports/investor presentations if non-US). Gather current share price, diluted share count, cash, debt, and consensus NTM (next-twelve-month) metrics. Calculate EV = Market Cap + Debt - Cash. Ensure currency consistency (e.g. convert to Euros if analyzing European operations).
        Step 3: Execute valuation models explicitly matching the Phase {phase_num} methodologies and industry overrides below.
        Step 4: Generate output using the exact layout below. Separate blocks with '---'. Do not add conversational intro text.

        ### VALUATION ALGORITHMIC FRAMEWORK BY LIFECYCLE PHASE
        - **Phase 1 (Startup):** Primary: FWD P/S (Guidance/Consensus). Secondary: P/GP. Peer set comparison.
        - **Phase 2 (Rapid Growth):** Primary: EV/Sales. Secondary: FWD P/S.
        - **Phase 3 (Solid Growth):** Primary: P/Sales. Secondary: EV/EBITDA (NTM).
        - **Phase 4 (Maturity):** Primary: Discounted Cash Flow (DCF) (5-10yr explicit + perpetuity). Secondary: FWD P/E. Must state clearly if it is 'Undervalued', 'Fairly Valued', or 'Overvalued'.
        - **Phase 5 (Declining):** Primary: Sum-of-the-Parts (SOTP) / Net Asset Value (NAV). Secondary: Reverse DCF / Liquidation Value / Dividend Yield vs Risk-Free Rate.

        ### INDUSTRY / ASSAY-SPECIFIC OVERRIDES
        - **Biotech / Life Sciences:** Probability-adjusted NPV (pNPV) of clinical pipeline using success probabilities. EV/Peak Sales. Green if Market Cap <= 0.7x pNPV; Yellow 0.7-1.3x; Red >= 1.3x.
        - **SaaS / Software:** Apply Rule of 40 (Growth % + FCF %). Evaluate EV/Gross Profit, FWD P/S, and Net Dollar Retention.
        - **Energy / Mining:** Net Asset Value (NAV/NPV) of reserves, SOTP by asset tier, EV/Reserves.
        - **Bitcoin / Crypto Treasury Companies:** Determine current market Net Asset Value (mNAV) and benchmark to peers.

        ### BENCHMARK COLOR RULES
        - 🟩 Green (Undervalued / Strong): Multiple <= peer 25th percentile OR <= company's own 3-year low.
        - 🟨 Yellow (Within Normal Range / Fair): Multiple between peer 25th and 75th percentile.
        - 🟥 Red (Overvalued / Weak): Multiple >= peer 75th percentile OR >= company's 3-year high.

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
            ## 👥 NETWORK EFFECT
            **Assessment:** [Present ✅ / Not Present ❌]
            ## ⚓ SWITCHING COSTS
            **Assessment:** [Present ✅ / Not Present ❌]
            ## 🏭 LOW-COST PRODUCTION
            **Assessment:** [Present ✅ / Not Present ❌]
            ## 🚀 COUNTER POSITIONING
            **Assessment:** [Present ✅ / Not Present ❌]
            ## 🏆 INTANGIBLE ASSETS
            **Assessment:** [Present ✅ / Not Present ❌]
            === PANEL_2_END ===

    # ==================================================================
    # 🧠 PANEL #8: SYSTEM SYNTHESIS & SCORING ENGINE (Sensitivity Adjusted)
    # ==================================================================
    
    # 1. Linguistic Parsing & Feature Extraction via Vector Synonyms
    has_moat_narrow_or_mod = contains_any(p2_output, ["narrow", "moderate", "⚖️", "➖"])
    moat_narrowing = contains_any(p2_output, ["narrowing", "decreasing", "eroding", "❌"])
    
    growth_potential_mod_or_low = contains_any(p3_output, ["moderate", "low", "➖", "❌"])
    growth_stable_or_decel = contains_any(p3_output, ["stable", "decelerating", "slowing", "➖", "❌"])
    
    metrics_poor = contains_any(p4_output, ["weak", "poor", "🔴", "0/10", "1/10", "2/10"])
    risk_high = contains_any(p5_output, ["high risk", "high level of risk", "🔴"])

    # Baseline parsing for deep dive/watchlist qualifications
    has_moat_valid = contains_any(p2_output, ["narrow", "wide", "moderate", "substantial", "economic moat"])
    moat_widening = contains_any(p2_output, ["widening", "increasing", "growing moat", "✅"])
    high_growth_potential = contains_any(p3_output, ["high", "exceptional", "strong growth potential", "✅"])
    growth_accelerating = contains_any(p3_output, ["accelerating", "speeding up", "inflection", "✅"])
    metrics_pass = contains_any(p4_output, ["good", "average", "strong", "moderate", "🟢", "🟡"])
    risk_acceptable = contains_any(p5_output, ["low risk", "medium risk", "moderate risk", "🟢", "🟡"])
    financials_acceptable = contains_any(p6_output, ["strong", "okay", "moderate", "robust", "healthy"])
    valuation_fair_or_under = contains_any(p7_output, ["undervalued", "fairly valued", "fair value", "under-valued", "🟢", "🟡"])

    # 2. Hard Gatekeeper Assessment (Priority Rejections)
    calculated_status = None
    rule_justification = ""

    # Phase Hard passes (Not Good Enough)
    if phase_num in ["1", "5"]:
        calculated_status = "❌ PASS (Not Good Enough)"
        rule_justification = f"Company is structurally limited by its business life cycle phase (Phase {phase_num} - Startup/Declining)."

    # Too Risky Hard Pass: Poor metrics combined with High Risk
    elif metrics_poor and risk_high:
        calculated_status = "❌ PASS (Too Risky)"
        rule_justification = "Fatal structural risk profile: Execution risk is high and key financial/operational metrics are tracking poorly."

    # Not Good Enough Hard Pass: Weakening Moat Dynamics
    elif has_moat_narrow_or_mod and moat_narrowing:
        calculated_status = "❌ PASS (Not Good Enough)"
        rule_justification = "Competitive erosion detected: The company holds only a narrow or moderate economic moat that is currently narrowing."

    # Not Good Enough Hard Pass: Weak or Flatlined Growth Runway
    elif growth_potential_mod_or_low and growth_stable_or_decel:
        calculated_status = "❌ PASS (Not Good Enough)"
        rule_justification = "Insufficient growth runway: Future growth potential is locked at moderate/low with a stable or decelerating velocity profile."

    # 3. Qualification Framework Evaluation Flow (If Hard Passes are Cleared)
    if calculated_status is None:
        if phase_num in ["2", "3"]:
            # Early Stage Growth Rule: Valuation is ignored completely
            if (has_moat_valid and moat_widening and high_growth_potential and 
                growth_accelerating and metrics_pass and risk_acceptable and financials_acceptable):
                calculated_status = "🚀 DEEP DIVE ASAP"
                rule_justification = f"Phase {phase_num} Early Growth Play matching all structural moat expansion, growth velocity, and foundational risk criteria (Valuation filter bypassed)."
            else:
                calculated_status = "⏳ ADD TO WATCHLIST"
                rule_justification = f"Phase {phase_num} Growth asset, but missing premium acceleration metrics. Tracked for pipeline timing changes."
            ---

        elif phase_num == "4":
            # Maturity Phase Rule: Fundamentals must pass AND valuation must be fair or undervalued
            if (has_moat_valid and moat_widening and high_growth_potential and 
                growth_accelerating and metrics_pass and risk_acceptable and financials_acceptable):
                
                if valuation_fair_or_under:
            === PANEL_3_START ===
            # 🚀 Future Growth Analysis: [Company Name] ({ticker}) 
            
            ### Future Growth Potential: [Select one: High ✅ / Moderate ➖ / Low ❌]
            ### Future Growth Direction: [Select one: Accelerating ✅ / Stable ➖ / Decelerating ❌]
            
            **Evidence Summary:** [1–2 sentence narrative supported by a defining corporate growth metric citation.] 

            ## 🌍 Market Expansion
            **Assessment:** Strength: [🟢/🟡/🔴/⚫] | Direction: [✅/➖/❌]
            ## 🧪 Product Innovation
            **Assessment:** Strength: [🟢/🟡/🔴/⚫] | Direction: [✅/➖/❌]
            ## 🤖 Technology Adoption
            **Assessment:** Strength: [🟢/🟡/🔴/⚫] | Direction: [✅/➖/❌]
            ## ⚖️ Regulatory Tailwinds
            **Assessment:** Strength: [🟢/🟡/🔴/⚫] | Direction: [✅/➖/❌]
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
            ### 🥷 Disruption
            - **Rating:** [🔴/🟡/🟢] | **Trend:** [⬆️/➖/⬇️]
            ### 🕵️ Outside Forces
            - **Rating:** [🔴/🟡/🟢] | **Trend:** [⬆️/➖/⬇️]
            ### 👥 Competition
            - **Rating:** [🔴/🟡/🟢] | **Trend:** [⬆️/➖/⬇️]
            === PANEL_5_END ===

            ---

            === PANEL_6_START ===
            # 📊 Financial Health Analysis: [Company Name] ({ticker})
            ## ✅ Overall Summary
            - **Overall Financial Health:** [Strong / Moderate / Weak / Okay]
            
            ## 🔍 Detailed Analysis 
            ### 📋 Income Statement
            - **Revenue Trend:** [⬆️/➖/⬇️] | **Score:** [🔴/🟡/🟢]
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
        # 📈 BATCH 3: Dynamic Metrics & Valuation Layer
        # ==================================================================
        p4_output = ""
        p7_output = ""
        with st.spinner(f"🔢 Running valuation math specifically targeted to Phase {phase_num}..."):
            metrics_valuation_prompt = f"""
            CRITICAL OPERATIONAL INSTRUCTION: You are an expert financial analyst evaluating corporate fundamentals for target: '{ticker}' mapped against corporate lifecycle Phase: '{phase_num}'.
            Step 1: Use your Google Search tool to find today's current date and year (2026).
            Step 2: Source recent filings (10-Q/10-K or international IR Annual Reports/investor presentations if non-US). Gather current share price, diluted share count, cash, debt, and consensus NTM (next-twelve-month) metrics. Calculate EV = Market Cap + Debt - Cash. Ensure currency consistency (e.g. convert to Euros if analyzing European operations).
            Step 3: Execute valuation models explicitly matching the Phase {phase_num} methodologies and industry overrides below.
            Step 4: Generate output using the exact layout below. Separate blocks with '---'. Do not add conversational intro text.

            ### VALUATION ALGORITHMIC FRAMEWORK BY LIFECYCLE PHASE
            - **Phase 1 (Startup):** Primary: FWD P/S (Guidance/Consensus). Secondary: P/GP. Peer set comparison.
            - **Phase 2 (Rapid Growth):** Primary: EV/Sales. Secondary: FWD P/S.
            - **Phase 3 (Solid Growth):** Primary: P/Sales. Secondary: EV/EBITDA (NTM).
            - **Phase 4 (Maturity):** Primary: Discounted Cash Flow (DCF) (5-10yr explicit + perpetuity). Secondary: FWD P/E. Must state clearly if it is 'Undervalued', 'Fairly Valued', or 'Overvalued'.
            - **Phase 5 (Declining):** Primary: Sum-of-the-Parts (SOTP) / Net Asset Value (NAV). Secondary: Reverse DCF / Liquidation Value / Dividend Yield vs Risk-Free Rate.

            ### INDUSTRY / ASSAY-SPECIFIC OVERRIDES
            - **Biotech / Life Sciences:** Probability-adjusted NPV (pNPV) of clinical pipeline using success probabilities. EV/Peak Sales. Green if Market Cap <= 0.7x pNPV; Yellow 0.7-1.3x; Red >= 1.3x.
            - **SaaS / Software:** Apply Rule of 40 (Growth % + FCF %). Evaluate EV/Gross Profit, FWD P/S, and Net Dollar Retention.
            - **Energy / Mining:** Net Asset Value (NAV/NPV) of reserves, SOTP by asset tier, EV/Reserves.
            - **Bitcoin / Crypto Treasury Companies:** Determine current market Net Asset Value (mNAV) and benchmark to peers.

            ### BENCHMARK COLOR RULES
            - 🟩 Green (Undervalued / Strong): Multiple <= peer 25th percentile OR <= company's own 3-year low.
            - 🟨 Yellow (Within Normal Range / Fair): Multiple between peer 25th and 75th percentile.
            - 🟥 Red (Overvalued / Weak): Multiple >= peer 75th percentile OR >= company's 3-year high.

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
        has_moat_narrow_or_mod = contains_any(p2_output, ["narrow", "moderate", "⚖️", "➖"])
        moat_narrowing = contains_any(p2_output, ["narrowing", "decreasing", "eroding", "❌"])
        growth_potential_mod_or_low = contains_any(p3_output, ["moderate", "low", "➖", "❌"])
        growth_stable_or_decel = contains_any(p3_output, ["stable", "decelerating", "slowing", "➖", "❌"])
        metrics_poor = contains_any(p4_output, ["weak", "poor", "🔴", "0/10", "1/10", "2/10"])
        risk_high = contains_any(p5_output, ["high risk", "high level of risk", "🔴"])

        has_moat_valid = contains_any(p2_output, ["narrow", "wide", "moderate", "substantial", "economic moat"])
        moat_widening = contains_any(p2_output, ["widening", "increasing", "growing moat", "✅"])
        high_growth_potential = contains_any(p3_output, ["high", "exceptional", "strong growth potential", "✅"])
        growth_accelerating = contains_any(p3_output, ["accelerating", "speeding up", "inflection", "✅"])
        metrics_pass = contains_any(p4_output, ["good", "average", "strong", "moderate", "🟢", "🟡"])
        risk_acceptable = contains_any(p5_output, ["low risk", "medium risk", "moderate risk", "🟢", "🟡"])
        financials_acceptable = contains_any(p6_output, ["strong", "okay", "moderate", "robust", "healthy"])
        valuation_fair_or_under = contains_any(p7_output, ["undervalued", "fairly valued", "fair value", "under-valued", "🟢", "🟡"])

        calculated_status = None
        rule_justification = ""

        if phase_num in ["1", "5"]:
            calculated_status = "❌ PASS (Not Good Enough)"
            rule_justification = f"Company is structurally limited by its business life cycle phase (Phase {phase_num} - Startup/Declining)."
        elif metrics_poor and risk_high:
            calculated_status = "❌ PASS (Too Risky)"
            rule_justification = "Fatal structural risk profile: Execution risk is high and key financial/operational metrics are tracking poorly."
        elif has_moat_narrow_or_mod and moat_narrowing:
            calculated_status = "❌ PASS (Not Good Enough)"
            rule_justification = "Competitive erosion detected: The company holds only a narrow or moderate economic moat that is currently narrowing."
        elif growth_potential_mod_or_low and growth_stable_or_decel:
            calculated_status = "❌ PASS (Not Good Enough)"
            rule_justification = "Insufficient growth runway: Future growth potential is locked at moderate/low with a stable or decelerating velocity profile."

        if calculated_status is None:
            if phase_num in ["2", "3"]:
                if (has_moat_valid and moat_widening and high_growth_potential and 
                    growth_accelerating and metrics_pass and risk_acceptable and financials_acceptable):
calculated_status = "🚀 DEEP DIVE ASAP"
                    rule_justification = "Phase 4 Mature asset meeting premium criteria with a clear valuation margin of safety (Fairly Valued / Undervalued)."
                    rule_justification = f"Phase {phase_num} Early Growth Play matching all structural moat expansion, growth velocity, and foundational risk criteria (Valuation filter bypassed)."
else:
calculated_status = "⏳ ADD TO WATCHLIST"
                    rule_justification = "Cleared quality bars, but flagged as Overvalued for a Phase 4 profile. Placed on Watchlist to await entry price."
                    rule_justification = f"Phase {phase_num} Growth asset, but missing premium acceleration metrics. Tracked for pipeline timing changes."
            elif phase_num == "4":
                if (has_moat_valid and moat_widening and high_growth_potential and 
                    growth_accelerating and metrics_pass and risk_acceptable and financials_acceptable):
                    if valuation_fair_or_under:
                        calculated_status = "🚀 DEEP DIVE ASAP"
                        rule_justification = "Phase 4 Mature asset meeting premium criteria with a clear valuation margin of safety (Fairly Valued / Undervalued)."
                    else:
                        calculated_status = "⏳ ADD TO WATCHLIST"
                        rule_justification = "Cleared quality bars, but flagged as Overvalued for a Phase 4 profile. Placed on Watchlist to await entry price."
                else:
                    calculated_status = "❌ PASS (Not Good Enough)"
                    rule_justification = "Phase 4 mature profile failing to meet core structural framework requirements."
else:
                calculated_status = "❌ PASS (Not Good Enough)"
                rule_justification = "Phase 4 mature profile failing to meet core structural framework requirements."
        else:
            calculated_status = "⏳ ADD TO WATCHLIST"
            rule_justification = "System fallback logic triggered. Placed on watchlist for manual evaluation."
                calculated_status = "⏳ ADD TO WATCHLIST"
                rule_justification = "System fallback logic triggered. Placed on watchlist for manual evaluation."

    # 4. Chief Investment Officer Panel Generation
    with st.expander("⚖️ Panel #8: Final Investment Decision", expanded=True):
        st.write("*Synthesizing framework layers into a final allocation recommendation...*")
        
        p8_prompt = f"""
        CRITICAL OPERATIONAL INSTRUCTION: You are the Chief Investment Officer of a boutique equity fund specialising in microeconomic moats and structural corporate lifecycles. Your job is to specialize the data gathered across our research framework for target asset: '{ticker}' (Phase Context: Phase {phase_num}).
        with st.expander("⚖️ Panel #8: Final Investment Decision", expanded=True):
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
           - **Core Investment Thesis:** Strongly highlight exactly why this asset presents an exceptional opportunity (the microeconomic moats, lifecycle expansion momentum, and core drivers). If Phase 2/3, highlight why valuation is ignored in favor of growth velocity. If Phase 4, explicitly highlight the valuation discipline.
           - **Key Risks to Identify:** Explicitly map out the asymmetric blindspots, complex operational risk elements, or structural assumptions the analyst must verify or clear.

        2. If the status is "⏳ ADD TO WATCHLIST":
           - **Core Investment Thesis:** Explain what is structurally preventing this asset from unlocking an immediate Deep Dive recommendation right now (e.g., waiting on valuation adjustments for mature plays, or scale/velocity attributes for earlier phase compounders).
           - **Key Risks to Identify:** Identify precisely what fundamental benchmark shifts, valuation thresholds, or corporate operational changes need to be met for this asset to become fully worthy of active investment attention.

        3. If the status is "❌ PASS (Too Risky)":
           - **Core Investment Thesis:** Clearly diagnose that this asset failed the safety audit. Focus heavily on why the combination of toxic risk exposure and bleeding core metrics creates a permanent destruction of capital risk, completely invalidating any potential growth narrative.
           - **Key Risks to Identify:** Outline the specific systemic risk factors, balance sheet or execution vulnerabilities that make this target completely uninvestable.

        4. If the status is "❌ PASS (Not Good Enough)":
           - **Core Investment Thesis:** Focus entirely on structural mediocrity. Explain that while the asset might not go bankrupt tomorrow, it represents a dead-capital trap due to stagnant revenue lines, a narrowing or weak economic moat, or decay in underlying industry lifecycles.
           - **Key Risks to Identify:** Highlight the risk of opportunity cost—tying up equity capital in low-velocity, deteriorating business profiles with zero macro tailwinds.

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

    st.success("✅ Full Framework Audit complete. Final recommendation engine active.")

# ------------------------------------------------------------------
# 🔄 RESET RUNTIME CONTROLS
# ------------------------------------------------------------------
st.write("---")
if st.button("🔄 Clear Dashboard & Run New Ticker"):
    st.rerun()
            The rules-based engine has already run a structural compliance check on this asset and determined the following mandatory designation:
            
            MANDATORY DESIGNATION: {calculated_status}
            SYSTEM REASONING: {rule_justification}

            You MUST accept this designation. Your role is to write the executive synthesis explaining the qualitative 'Why' behind this decision, utilizing the findings from our individual modules.

            Output ONLY the markdown format below. Ensure the layout matches perfectly. Use the specific HTML structure provided below for the Final Recommendation to make it pop out with massive text and clear separation.

            # ⚖️ Assessment Summary: {ticker}
            <div style="background-color: rgba(255, 255, 255, 0.05); padding: 15px; border-left: 5px solid #ff4b4b; border-radius: 4px; margin: 15px 0;">
                <h2 style="margin: 0; padding: 0; font-size: 28px; font-weight: 800; letter-spacing: 0.5px;">
                    Final Recommendation: {calculated_status}
                </h2>
            </div>

            **Core Investment Thesis (The \"Why\"):** [A punchy, single-sentence summary validating the system reasoning: '{rule_justification}']

            ### 📋 Core Investment Thesis & Risks
            - **Core Investment Thesis:** [Provide a detailed 2-3 sentence strategic rationale customized to the designation parameters.]
            - **Key Risks to Identify:** [Provide a detailed 2-3 sentence breakdown customized to the designation parameters.]

            ### 🛠️ Required Next Steps
            - **Primary Blindspot to Verify:** [Identify the #1 operational metric or data point needed to monitor this decision.]
            - **Trigger Condition:** [Define a clear operational or valuation trigger to either archive, monitor, or buy this stock.]
            """
            try:
                final_decision = generate_analysis_layer(ticker, p8_prompt)
                st.markdown(final_decision, unsafe_allow_html=True)
            except Exception as e:
                st.error(f"Error executing Panel 8 Logic Layer: {e}")

        st.success("✅ Full Framework Audit complete. Final recommendation engine active.")

    # ------------------------------------------------------------------
    # 🔄 RESET RUNTIME CONTROLS
    # ------------------------------------------------------------------
    st.write("---")
    if st.button("🔄 Clear Dashboard & Run New Ticker"):
        st.rerun()
