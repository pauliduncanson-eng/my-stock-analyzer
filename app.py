import streamlit as st
import re
from google import genai
from google.genai import types

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

# 3. Optimized API Call Wrapper with Caching
@st.cache_data(show_spinner=False)
def generate_analysis_layer(ticker, prompt_text):
    config = types.GenerateContentConfig(
        tools=[{"google_search": {}}],
        temperature=0.2,
    )
    response = client.models.generate_content(
        model="gemini-2.5-flash", 
        contents=prompt_text, 
        config=config
    )
    return response.text

# Helper function to extract the single digit phase number from the model's text output
def extract_phase_number(text):
    match = re.search(r'\b(Phase\s*([1-5])|([1-5])\b)', text, re.IGNORECASE)
    if match:
        # Return the captured digit
        return match.group(2) if match.group(2) else match.group(3)
    return "3"  # Fallback baseline to Solid Growth if the text doesn't explicitly match

# 4. User Input Interface
with st.form(key="research_panel_form"):
    ticker = st.text_input("Enter Stock Ticker Symbol (e.g., TSLA, ASML, NVDA):", "").strip().upper()
    submit_button = st.form_submit_button(label="🚀 Run Full Framework Audit")

# 5. Run Analysis Framework Upon Submission
if submit_button and ticker:
    st.info(f"Analyzing {ticker}... Pulling primary filings, establishing lifecycle phase, and processing framework panels.")

    # ------------------------------------------------------------------
    # 🧭 PANEL #1: Business Phase Analysis (The Core Foundation)
    # ------------------------------------------------------------------
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

    # ------------------------------------------------------------------
    # 🏰 PANEL #2: Moat Analysis v3
    # ------------------------------------------------------------------
    with st.expander("🏰 Moat Analysis v3", expanded=True):
        st.write("*Evaluating structural microeconomic competitive moats...*")
        p2_prompt = f"""
        CRITICAL OPERATIONAL INSTRUCTION: You are a world-class financial analyst specialising in Business Moat Assessment. Your target stock ticker is: '{ticker}'.
        Step 1: Use your Google Search tool to identify today's current date and year. 
        Step 2: Search SEC EDGAR, official Company Investor Relations pages, and institutional research to locate the most recent 10-K, 10-Q, or international Annual Reports, plus recent earnings call transcripts for ticker '{ticker}'.
        Step 3: Evaluate the company against the following MOAT SIZE & DIRECTION CRITERIA, starting with a default baseline assumption of "No Moat" until hard positive evidence proves otherwise.
        MOAT SIZE CRITERIA: WIDE MOAT (>10 years durability), MODERATE MOAT, NARROW MOAT (1-3 years durability), NO MOAT.
        MOAT DIRECTION CRITERIA: Widening, Stable, Narrowing.
        Step 4: Generate your output using the exact markdown template below. Do not add any conversational preambles. Output ONLY the completed template:

        # 🏰 MOAT ANALYSIS: [Company Name] ({ticker})
        **Moat size:** [Select one: None ❌, Narrow ➖, Moderate ⚖️, Wide ✅]
        **Moat direction:** [Select one: Widening ✅ / Stable ➖ / Narrowing ❌]
        **Primary moat sources:** [List the 1-2 most dominant moat sources, prepending an appropriate emoji like 👥 for Network Effect, ⚓ for Switching Costs, 🏭 for Low-Cost Production, 🚀 for Counter Positioning, or 🏆 for Intangible Assets]
        **Summary:** [Provide a 1-2 sentence summary of the Moat thesis, supported by a key metric citation.]

        ## 👥 NETWORK EFFECT
        **Assessment:** [Present ✅ / Not Present ❌] -> [If present, output Size and Direction with emojis]
        **Analysis:** [Provide a detailed paragraph explaining the reasoning for your network effect assessment.]
        **Supporting Data:** 
        - [Metric 1]
        - [Metric 2]
        **Evidence Quote:** "[Provide a direct quote from recent filings or transcripts]"

        ## ⚓ SWITCHING COSTS
        **Assessment:** [Present ✅ / Not Present ❌] -> [If present, output Size and Direction with emojis]
        **Analysis:** [Provide a paragraph explaining the reasoning for your switching costs assessment.]
        **Supporting Data:** 
        - [Metric 1]
        **Evidence Quote:** "[Provide a direct quote describing how customers are locked-in]"

        ## 🏭 LOW-COST PRODUCTION
        **Assessment:** [Present ✅ / Not Present ❌] -> [If present, output Size and Direction with emojis]
        **Analysis:** [Provide a detailed paragraph explaining the reasoning for your low-cost production assessment.]
        **Supporting Data:** 
        - [Metric 1]
        **Evidence Quote:** "[Provide a direct quote]"

        ## 🚀 COUNTER POSITIONING
        **Assessment:** [Present ✅ / Not Present ❌] -> [If present, output Size and Direction with emojis]
        **Analysis:** [Provide a detailed paragraph explaining the reasoning for your counter positioning assessment.]
        **Supporting Data:** 
        - [Metric 1]
        **Evidence Quote:** "[Provide a direct quote]"

        ## 🏆 INTANGIBLE ASSETS
        **Assessment:** [Present ✅ / Not Present ❌] -> [If present, output Size and Direction with emojis]
        **Analysis:** [Provide a detailed paragraph explaining the reasoning for your intangible assets assessment.]
        **Supporting Data:** 
        - [Metric 1]
        **Evidence Quote:** "[Provide a direct quote showcasing brand equity or patent strength]"

        ## ⚠️ Risks & Competitive Landscape
        - **Primary Moat Risk:** [Identify threat to moat with a cited data point.]
        - **Competitive Threat Summary:** [Briefly describe main active competitors.]
        - **Valuation Context:** [Provide current core valuation metrics compared to historical or peer averages.]
        - **Institutional/Analyst View Comparison:** [Summarize institutional views vs your first-principles analysis.]

        ## 🔗 Sources Used
        [1] [Exact name of primary filing or transcript used]
        """
        try:
            output = generate_analysis_layer(ticker, p2_prompt)
            st.markdown(output)
        except Exception as e:
            st.error(f"Error executing Panel 2: {e}")

    # ------------------------------------------------------------------
    # 🚀 PANEL #3: Business Growth Analysis v2.2
    # ------------------------------------------------------------------
    with st.expander("🚀 Business Growth Analysis v2.2", expanded=True):
        st.write("*Analyzing long-term organic and systemic growth drivers...*")
        p3_prompt = f"""
        CRITICAL OPERATIONAL INSTRUCTION: You are an expert growth strategist specializing in identifying and evaluating corporate growth mechanisms from financial filings. Your target stock ticker is: '{ticker}'.
        Step 1: Use your Google Search tool to identify today's current date and year. 
        Step 2: Search SEC EDGAR, official Company Investor Relations pages, and supplementary sources to locate the most recent filings for ticker '{ticker}'.
        Step 3: Evaluate the company strictly across the following 6 specified Growth Driver Categories: Market Expansion, Product Innovation, Technology Adoption, Regulatory Tailwinds, Strategic Partnerships & M&A, Operational Efficiency.
        Step 4: Grade each driver using these strict structural rules: Strength (🟢=Strong, 🟡=Moderate, 🔴=Weak, ⚫=N/A) | Direction (✅=Accelerating, ➖=Stable, ❌=Decelerating).
        Step 5: Generate your output using the exact template below. Do not add any conversational filler. Output ONLY the completed template:

        # 🚀 Future Growth Analysis: [Company Name] ({ticker}) 
        **Growth Potential:** [Select one: High ✅ / Moderate ➖ / Low ❌] 
        **Growth Direction:** [Select one: Accelerating ✅ / Stable ➖ / Decelerating ❌] 
        **Primary Growth Drivers:** [List top 2-3 categories with their emojis] 
        **Evidence Summary:** [1–2 sentence narrative supported by a defining corporate growth metric citation.] 

        ## 🌍 Market Expansion
        **Assessment:** Strength: [🟢/🟡/🔴/⚫] | Direction: [✅/➖/❌]
        **Supporting Data:** - [Core metric data]
        **Evidence:** [Data-driven narrative supported by a specific metric or direct management statement.] 

        ## 🧪 Product Innovation
        **Assessment:** Strength: [🟢/🟡/🔴/⚫] | Direction: [✅/➖/❌]
        **Supporting Data:** - [R&D Spend or intensity metrics]
        **Evidence:** [Data-driven narrative supported by a specific metric.] 

        ## 🤖 Technology Adoption
        **Assessment:** Strength: [🟢/🟡/🔴/⚫] | Direction: [✅/➖/❌]
        **Supporting Data:** - [Tech CapEx or operational metrics]
        **Evidence:** [Data-driven narrative.] 

        ## ⚖️ Regulatory Tailwinds
        **Assessment:** Strength: [🟢/🟡/🔴/⚫] | Direction: [✅/➖/❌]
        **Supporting Data:** - [Policy impact metric]
        **Evidence:** [Data-driven narrative.] 

        ## 🤝 Strategic Partnerships & M&A
        **Assessment:** Strength: [🟢/🟡/🔴/⚫] | Direction: [✅/➖/❌]
        **Supporting Data:** - [Transaction value or volume counts]
        **Evidence:** [Data-driven narrative.] 

        ## ⚙️ Operational Efficiency
        **Assessment:** Strength: [🟢/🟡/🔴/⚫] | Direction: [✅/➖/❌]
        **Supporting Data:** - [Margin expansion or savings metrics]
        **Evidence:** [Data-driven narrative.] 

        ## ⚠️ Risks & Final Considerations
        - **Primary Growth Risk:** [Identify and explain the most significant threat to growth, backed by a clear cited data point.]
        - **Competitive Landscape Overview:** [Brief narrative on market share dynamics.]
        - **Valuation Risk context:** [Core growth valuation metrics like forward P/E or PEG ratio vs closest peers.]

        ## 🔗 Sources Used
        [1] [Exact name of primary filing or transcript used]
        """
        try:
            output = generate_analysis_layer(ticker, p3_prompt)
            st.markdown(output)
        except Exception as e:
            st.error(f"Error executing Panel 3: {e}")

    # ------------------------------------------------------------------
    # 📊 PANEL #4: Key Metrics Analysis Rev 2.2 (Dynamic Routing)
    # ------------------------------------------------------------------
    with st.expander("📊 Business Key Metrics Analysis", expanded=True):
        st.write(f"*Running diagnostic metrics customized to automated Phase {phase_num} targets...*")
        p4_prompt = f"""
        CRITICAL OPERATIONAL INSTRUCTION: You are an expert financial analyst evaluating a company's phase-appropriate metrics using a strict Red/Yellow/Green framework. Target Stock Ticker: '{ticker}'. Target Corporate Phase: '{phase_num}'.
        Step 1: Use your Google Search tool to identify today's current date and year.
        Step 2: Locate the most recent financial files for ticker '{ticker}'.
        Step 3: Extract metrics (Revenue CAGR, Gross/Operating Margins, FCF, Dilution, ROIC) required to evaluate phase-specific thresholds.
        Step 4: Map performance numbers to Phase instruction metrics (Phase 1: PMF/Burn Rate | Phase 2: Growth/Rule of 40 | Phase 3: CAGR/ROIC | Phase 4: Mature FCF Yield/Dilution | Phase 5: Decline asset liquidation metrics).
        Step 5: Generate your output using the exact template below. Do not add any conversational remarks. Output ONLY the completed template:

        **Primary Phase:** [Insert phase classification here based on Phase Number requested]
        **Secondary Phase (if applicable):** [Optional]
        **Summary:** [Provide a clear, non-jargon, one-paragraph summary of the results written for a new investor.]

        | Metric Found | Actual Calculated Value | Benchmark Status (🔴/🟡/🟢) |
        | :--- | :--- | :--- |
        | [Insert Phase Metric 1 Name] | [Value] | [🔴/🟡/🟢] |
        | [Insert Phase Metric 2 Name] | [Value] | [🔴/🟡/🟢] |
        | [Insert Phase Metric 3 Name] | [Value] | [🔴/🟡/🟢] |
        | [Insert Phase Metric 4 Name] | [Value] | [🔴/🟡/🟢] |
        | [Insert Phase Metric 5 Name] | [Value] | [🔴/🟡/🟢] |

        **Overall Scoring Rating:** [Computed consensus rating, e.g., Mixed/Yellow or Highly Positive/Green]

        ## 🔗 Sources Used
        [1] [Exact name of core filing, statement, or transcript used]
        """
        try:
            output = generate_analysis_layer(ticker, p4_prompt)
            st.markdown(output)
        except Exception as e:
            st.error(f"Error executing Panel 4: {e}")

    # ------------------------------------------------------------------
    # ⚠️ PANEL #5: Business Risk Analysis v2.0
    # ------------------------------------------------------------------
    with st.expander("⚠️ Business Risk Analysis v2.0", expanded=True):
        st.write("*Scanning 1A Risk factors and exposure concentrations...*")
        p5_prompt = f"""
        CRITICAL OPERATIONAL INSTRUCTION: You are an expert risk analyst specializing in identifying and evaluating operational and strategic risks from corporate financial filings. Your target stock ticker is: '{ticker}'.
        Step 1: Use your Google Search tool to identify today's current date and year.
        Step 2: Search SEC EDGAR to locate the most recent 10-K (Item 1A Risk Factors) and recent 10-Q filings for ticker '{ticker}'.
        Step 3: Evaluate the company strictly across the following four critical risk dimensions: Concentration Risk, Disruption Risk, Outside Forces Risk, Competition Risk. Rating criteria: 🔴 Red, 🟡 Yellow, 🟢 Green.
        Step 4: Calculate the Overall Summary Risk Level via a strict weighted score equation: Red = 5 pts, Yellow = 2 pts, Green = 1 pt. Average = Sum / 4. High Risk >=2.5, Medium 1.5-2.4, Low <1.5.
        Step 5: Generate your output using the exact template below. Use bullets for evidence. Output ONLY the completed template:

        # ⚠️ Execution Risk Analysis: [Company Name] ({ticker})

        ## 📊 Overall Summary
        - **Overall Risk Level:** [High Risk 🔴 / Medium Risk 🟡 / Low Risk 🟢] (Based on calculated score of [Value])
        - **⚠️ Primary Risk Factors:** [List the highest risk pillars]
        - **🛡️ Key Mitigation:** [Highlight corporate defense asset or program mentioned in filings]

        ---

        ## 🎯 RISK ASSESSMENT DETAILS
        ### 🥚🧺 Concentration
        - **Rating:** [🔴/🟡/🟢] | **Trend:** [⬆️/➖/⬇️]
        - **Evidence:** [Provide 1 concise bullet point with inline filing citation]
        - **Mitigation:** [Summarize defensive strategy]

        ### 🥷 Disruption
        - **Rating:** [🔴/🟡/🟢] | **Trend:** [⬆️/➖/⬇️]
        - **Evidence:** [...]
        - **Mitigation:** [...]

        ### 🕵️ Outside Forces
        - **Rating:** [🔴/🟡/🟢] | **Trend:** [⬆️/➖/⬇️]
        - **Evidence:** [...]
        - **Mitigation:** [...]

        ### 👥 Competition
        - **Rating:** [🔴/🟡/🟢] | **Trend:** [⬆️/➖/⬇️]
        - **Evidence:** [...]
        - **Mitigation:** [...]

        ## 🔗 Sources Used
        [1] [Exact name and section of primary filing used]
        """
        try:
            output = generate_analysis_layer(ticker, p5_prompt)
            st.markdown(output)
        except Exception as e:
            st.error(f"Error executing Panel 5: {e}")

    # ------------------------------------------------------------------
    # 📊 PANEL #6: Financial Statement Analysis v1.1
    # ------------------------------------------------------------------
    with st.expander("📊 Financial Statement Analysis v1.1", expanded=True):
        st.write("*Parsing core financial statements from original regulatory databases...*")
        p6_prompt = f"""
        CRITICAL OPERATIONAL INSTRUCTION: You are an expert financial analyst evaluating corporate financial health using ONLY official 10-K and 10-Q statements. Your target stock ticker is: '{ticker}'.
        Step 1: Identify today's current year via a web search if necessary. 
        Step 2: Access official regulatory data to extract the most recent 10-K and 10-Q financial statements for ticker '{ticker}'.
        Step 3: Evaluate Income Statement, Balance Sheet, and Cash Flow metrics vs prior year period. Score items as 🔴, 🟡, or 🟢.
        Step 4: Generate output using the exact template below. Do not add conversational remarks. Output ONLY the completed template:

        # 📊 Financial Health Analysis: [Company Name] ({ticker})
        ## ✅ Overall Summary
        - **Overall Financial Health:** [Strong / Moderate / Weak]
        - **Key Positive Indicators:** [List top specific financial strengths]
        - **Key Concerns:** [List top specific weaknesses]

        ---
        ## 🔍 Detailed Analysis 
        ### 📋 Income Statement
        - **Revenue Trend:** [⬆️/➖/⬇️] | **Score:** [🔴/🟡/🟢] | *Evidence:* [Brief text with citation]
        - **Gross Profit Trend:** [⬆️/➖/⬇️] | **Score:** [🔴/🟡/🟢] | *Evidence:* [...]
        - **Operating Income Trend:** [⬆️/➖/⬇️] | **Score:** [🔴/🟡/🟢] | *Evidence:* [...]
        - **EPS Trend:** [⬆️/➖/⬇️] | **Score:** [🔴/🟡/🟢] | *Evidence:* [...]
        - **Summary Score (Income Statement):** [🔴 / 🟡 / 🟢]

        ### 🏦 Balance Sheet
        - **Cash & Securities:** [⬆️/➖/⬇️] | **Score:** [🔴/🟡/🟢] | *Evidence:* [...]
        - **Debt Levels:** [⬆️/➖/⬇️] | **Score:** [🔴/🟡/🟢] | *Evidence:* [...]
        - **Summary Score (Balance Sheet):** [🔴 / 🟡 / 🟢]

        ### 💸 Cash Flows
        - **Free Cash Flow:** [⬆️/➖/⬇️] | **Score:** [🔴/🟡/🟢] | *Evidence:* [...]
        - **Operating Cash Flow:** [⬆️/➖/⬇️] | **Score:** [🔴/🟡/🟢] | *Evidence:* [...]
        - **Summary Score (Cash Flow):** [🔴 / 🟡 / 🟢]

        ## 🔗 Sources Used
        [1] [Filing identifier from official source]
        """
        try:
            output = generate_analysis_layer(ticker, p6_prompt)
            st.markdown(output)
        except Exception as e:
            st.error(f"Error executing Panel 6: {e}")

    # ------------------------------------------------------------------
    # 💰 PANEL #7: Business Valuation Analysis (Dynamic Routing)
    # ------------------------------------------------------------------
    with st.expander("💰 Business Valuation Analysis", expanded=True):
        st.write(f"*Running automated metrics tailored specifically to Phase {phase_num} parameters...*")
        p7_prompt = f"""
        CRITICAL OPERATIONAL INSTRUCTION: You are an expert equity analyst applying the appropriate valuation methodology for a company's specific lifecycle business phase using a strict benchmarking framework. Target Stock Ticker: '{ticker}'. Target Corporate Phase: '{phase_num}'.
        Step 1: Use your Google Search tool to identify today's current date and year.
        Step 2: Locate the most recent regulatory filings and consensus data for ticker '{ticker}'.
        Step 3: Execute calculations strictly aligned to Phase parameters: Phase 1 (Forward P/S), Phase 2 (EV/Sales), Phase 3 (P/S & EV/EBITDA), Phase 4 (DCF/Reverse DCF), Phase 5 (Liquidation Asset-Backed valuation).
        Step 4: Output your detailed phase-appropriate valuation layout clearly using markdown metrics. Do not include conversational preambles.
        """
        try:
            output = generate_analysis_layer(ticker, p7_prompt)
            st.markdown(output)
        except Exception as e:
            st.error(f"Error executing Panel 7: {e}")
            
    # ------------------------------------------------------------------
    # 🧠 PANEL #8: SYSTEM SYNTHESIS & SCORING ENGINE
    # ------------------------------------------------------------------
    
    # 1. Variable Extraction & Standardization
    try:
        current_phase = phase_output.strip().lower()       
        risk_level = output.strip().lower() if 'output' in locals() else "unknown"        
        growth_potential = output.strip().lower() if 'output' in locals() else "unknown"   
        is_small_cap = True  # Baseline safeguard for micro-caps
    except Exception as parse_err:
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

        You MUST accept this designation. Your role is to write the executive synthesis explaining the qualitative 'Why' behind this decision, utilizing the findings from our individual modules:
        - MOAT PROFILE: Size and direction of competitive advantages.
        - GROWTH DYNAMICS: Organic expansion vs. capital efficiency.
        - KEY PERFORMANCE METRICS: Red/Yellow/Green health signals.
        - RISK PROFILE: Execution threats and concentration risks.

        Generate your final executive summary using the exact template below. Do not add any conversational preambles:

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
