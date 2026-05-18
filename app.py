import streamlit as st
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

client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])

# 3. User Input Interface (Updated to include Phase Dropdown)
col1, col2 = st.columns([2, 1])
with col1:
    ticker = st.text_input("Enter Stock Ticker Symbol (e.g., TSLA, ASML, NVDA):", "").strip().upper()
with col2:
    phase_selection = st.selectbox(
        "Select Business Phase:",
        ["Phase 1: Startup 💡", "Phase 2: Rapid Growth 🚀", "Phase 3: Solid Growth 📈", "Phase 4: Maturity 🏦", "Phase 5: Decline 📉"]
    )

# Extract just the single number character from the dropdown selection string (e.g., "1")
phase_num = phase_selection.split(":")[0][-1]

    #------------------------------------------------------------------
    # 🔴 PROMPT #1: Business Phase Analysis (Optimised for your tool)
    # ------------------------------------------------------------------
    with st.expander("🧭 Business Phase Analysis", expanded=True):
        business_phase_prompt = f"""
        CRITICAL OPERATIONAL INSTRUCTION: You are a World-Class Strategic Analyst specialising in Business Lifecycle and Phase Identification. Your target stock ticker is: '{ticker}'. 

        Step 1: Use your Google Search tool to identify today's current date and year.
        Step 2: Search SEC EDGAR, official Company Investor Relations pages, and recent financial filings to locate the most recent 10-K, 10-Q, or international Annual Reports for ticker '{ticker}'.
        Step 3: Analyze the company's trajectory, revenue patterns, and product maturity. Classify it strictly into one of the following 5 phases:
        1. Startup (early product/market fit, not yet profitable)
        2. Rapid Growth (rapid scaling, profitable or near-profitable)
        3. Solid Growth (FCF positive, durable growth)
        4. Maturity (stable Free Cash Flows, normalized growth)
        5. Declining (shrinking revenue/earnings)

        Step 4: Output your final findings using the template format below. Do not add any conversational preambles or filler text. Output ONLY the completed template:

        # 🧭 Business Phase Analysis: [Company Name] ({ticker})
        **Identified Phase:** [Phase Number: Phase Name]
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
            response = client.models.generate_content(model="gemini-2.5-flash", contents=business_phase_prompt, config=config)
            st.markdown(response.text)
        except Exception as e:
            st.error(f"Error executing Business Phase Analysis: {e}")

    # ------------------------------------------------------------------
    # 🔴 PROMPT #2: Moat Analysis v3 (Optimized for your tool)
    # ------------------------------------------------------------------
    with st.expander("🏰 Moat Analysis v3", expanded=True):
        moat_analysis_prompt = f"""
        CRITICAL OPERATIONAL INSTRUCTION: You are a world-class financial analyst specialising in Business Moat Assessment. Your target stock ticker is: '{ticker}'.

        Step 1: Use your Google Search tool to identify today's current date and year. 
        Step 2: Search SEC EDGAR, official Company Investor Relations pages, and institutional research to locate the most recent 10-K, 10-Q, or international Annual Reports, plus recent earnings call transcripts for ticker '{ticker}'.
        Step 3: Evaluate the company against the following MOAT SIZE & DIRECTION CRITERIA, starting with a default baseline assumption of "No Moat" until hard positive evidence proves otherwise.

        MOAT SIZE CRITERIA:
        - WIDE MOAT (>10 years durability): Powerful network effects, severe switching costs, high customer appeal/pricing power brands, or structural lowest-cost production.
        - MODERATE MOAT: Strong growing network, moderate switching costs, rising brand appeal with some pricing power, or notable cost efficiencies.
        - NARROW MOAT (1-3 years durability): Niche network, minor frictional switching costs, brand loyalty vulnerable to price, or regionally limited cost advantages.
        - NO MOAT: Undifferentiated product, high customer churn, zero pricing power, or cost structures equal to or higher than peers.

        MOAT DIRECTION CRITERIA:
        - Widening: Rising user engagement, Gross Margin expansion, or EBITDA Margin expansion.
        - Stable: Flat growth/margins, high retention but no new competitive structural advantages.
        - Narrowing: Increasing customer churn, Gross Margin compression, or EBITDA Margin compression.

        Step 4: Generate your output using the exact markdown template below. Do not add any conversational preambles, introductory filler, or meta-commentary. Output ONLY the completed template:

        # 🏰 MOAT ANALYSIS: [Company Name] ({ticker})
        **Moat size:** [Select one: None ❌, Narrow ➖, Moderate ⚖️, Wide ✅]
        **Moat direction:** [Select one: Widening ✅ / Stable ➖ / Narrowing ❌]
        **Primary moat sources:** [List the 1-2 most dominant moat sources, prepending an appropriate emoji like 👥 for Network Effect, ⚓ for Switching Costs, 🏭 for Low-Cost Production, 🚀 for Counter Positioning, or 🏆 for Intangible Assets]
        **Summary:** [Provide a 1-2 sentence summary of the Moat thesis, supported by a key metric citation.]

        ## 👥 NETWORK EFFECT
        **Assessment:** [Present ✅ / Not Present ❌] -> [If present, output Size and Direction with emojis, e.g., Wide ✅, Widening ✅]
        **Analysis:** [Provide a detailed paragraph explaining the reasoning for your network effect assessment.]
        **Supporting Data:** 
        - [Metric 1: e.g., Customer/User Growth % YoY]
        - [Metric 2: e.g., Platform engagement or volume metrics]
        **Evidence Quote:** "[Provide a direct quote from recent filings or transcripts describing how new users add value to the network]"

        ## ⚓ SWITCHING COSTS
        **Assessment:** [Present ✅ / Not Present ❌] -> [If present, output Size and Direction with emojis]
        **Analysis:** [Provide a paragraph explaining the reasoning for your switching costs assessment.]
        **Supporting Data:** 
        - [Metric 1: e.g., Net Dollar Retention (NDR) %]
        - [Metric 2: e.g., Gross Customer Retention %]
        **Evidence Quote:** "[Provide a direct quote describing how customers are locked-in or structurally reliant on this business]"

        ## 🏭 LOW-COST PRODUCTION
        **Assessment:** [Present ✅ / Not Present ❌] -> [If present, output Size and Direction with emojis]
        **Analysis:** [Provide a detailed paragraph explaining the reasoning for your low-cost production assessment.]
        **Supporting Data:** 
        - [Metric 1: e.g., Current Gross Margin % vs peers]
        - [Metric 2: e.g., Operating Margin trend or Cost Per Unit advantage]
        **Evidence Quote:** "[Provide a direct quote describing why unit costs or production structures are lower than competitors]"

        ## 🚀 COUNTER POSITIONING
        **Assessment:** [Present ✅ / Not Present ❌] -> [If present, output Size and Direction with emojis]
        **Analysis:** [Provide a detailed paragraph explaining the reasoning for your counter positioning assessment.]
        **Supporting Data:** 
        - [Metric 1: e.g., Customer Acquisition Cost (CAC) dynamics vs incumbents]
        - [Metric 2: e.g., Margin/revenue damage an incumbent would suffer if they copied this model]
        **Evidence Quote:** "[Provide a direct quote describing why this business model is structurally hard for legacy incumbents to copy]"

        ## 🏆 INTANGIBLE ASSETS
        **Assessment:** [Present ✅ / Not Present ❌] -> [If present, output Size and Direction with emojis]
        **Analysis:** [Provide a detailed paragraph explaining the reasoning for your intangible assets assessment.]
        **Supporting Data:** 
        - [Metric 1: e.g., Return on Invested Capital (ROIC) %]
        - [Metric 2: e.g., Premium pricing spread over generic alternatives]
        **Evidence Quote:** "[Provide a direct quote showcasing brand equity, patent strength, or regulatory protection pricing power]"

        ## ⚠️ Risks & Competitive Landscape
        - **Primary Moat Risk:** [Identify and explain the most significant threat to this company's moat, supported by a cited data point.]
        - **Competitive Threat Summary:** [Briefly describe the main active competitors and how they are attacking this moat.]
        - **Valuation Context:** [Provide current core valuation metrics compared to historical or peer averages.]
        - **Institutional/Analyst View Comparison:** [Search for consensus or major institutional views on this company's moat. Summarize whether your first-principles analysis confirms, challenges, or adds nuance to their view.]

        ## 🔗 Sources Used
        [1] [Exact name of primary filing or transcript used]
        [2] [Exact name of secondary source or analyst report used]
        """
        try:
            response = client.models.generate_content(model="gemini-2.5-flash", contents=moat_analysis_prompt, config=config)
            st.write(response.text)
        except Exception as e:
            st.error(f"Error running Moat Analysis: {e}")


  # ------------------------------------------------------------------
    # 🔴 PROMPT #3: Business Growth Analysis v2.2 (Optimized for your tool)
    # ------------------------------------------------------------------
    with st.expander("🚀 Business Growth Analysis v2.2", expanded=True):
        growth_analysis_prompt = f"""
        CRITICAL OPERATIONAL INSTRUCTION: You are an expert growth strategist specializing in identifying and evaluating corporate growth mechanisms from financial filings and strategic initiatives. Your target stock ticker is: '{ticker}'.

        Step 1: Use your Google Search tool to identify today's current date and year. 
        Step 2: Search SEC EDGAR, official Company Investor Relations pages, and supplementary sources to locate the most recent 10-K, 10-Q, Annual Reports, recent earnings call transcripts, investor presentations, and analyst consensus commentary for ticker '{ticker}'.
        Step 3: Evaluate the company strictly across the following 6 specified Growth Driver Categories:
        - 🌍 Market Expansion: TAM growth, geographic penetration, international expansion.
        - 🧪 New Products/Services: R&D intensity, new product/service launches.
        - 🤖 Technology Adoption: AI integration, automation, internal digital transformations.
        - ⚖️ Regulatory Tailwinds: Favorable policy changes, subsidies, compliance tailwinds.
        - 🤝 Strategic Partnerships & M&A: Strategic alliances, joint ventures, acquisitions unlocking new horizons.
        - ⚙️ Operational Efficiency: Lean operations, structural margin improvement initiatives.

        Step 4: Grade each driver using these strict structural rules:
        - STRENGTH: 🟢=Strong (clear metrics/major investment), 🟡=Moderate (mentioned but not prioritized), 🔴=Weak (limited evidence), ⚫=Not applicable.
        - DIRECTION: ✅=Accelerating, ➖=Stable, ❌=Decelerating.
        - BASELINE ASSUMPTION: Assume a default position of "No Growth Driver" for each category until proven otherwise by hard data.

        Step 5: Generate your output using the exact template below. Do not add any conversational filler, intro preambles, or post-summary summaries. Output ONLY the completed template:

        # 🚀 Future Growth Analysis: [Company Name] ({ticker}) 
        **Growth Potential:** [Select one: High ✅ / Moderate ➖ / Low ❌] 
        **Growth Direction:** [Select one: Accelerating ✅ / Stable ➖ / Decelerating ❌] 
        **Primary Growth Drivers:** [List the top 2-3 most dominant categories from Step 3 with their emojis] 
        **Evidence Summary:** [1–2 sentence narrative supported by a defining corporate growth metric citation.] 

        ## 🌍 Market Expansion
        **Assessment:** Strength: [🟢/🟡/🔴/⚫] | Direction: [✅/➖/❌]
        **Supporting Data:**
        - TAM Growth/Metric: [X% or $X billion]
        - International/Segment Revenue Share: [X%]
        **Evidence:** [1–2 sentence clear data-driven narrative supported by a specific metric or direct management statement.] 

        ## 🧪 Product Innovation
        **Assessment:** Strength: [🟢/🟡/🔴/⚫] | Direction: [✅/➖/❌]
        **Supporting Data:**
        - R&D Spend / Intensity: [$X million or X% of revenue]
        - New Pipeline Launch Metrics: [Details on recent product rollouts]
        **Evidence:** [1–2 sentence clear data-driven narrative supported by a specific metric or direct management statement.] 

        ## 🤖 Technology Adoption
        **Assessment:** Strength: [🟢/🟡/🔴/⚫] | Direction: [✅/➖/❌]
        **Supporting Data:**
        - Tech Capital Expenditure / Savings: [Metrics showing scale of adoption]
        - Operational Impact Metric: [Performance or efficiency lift metrics]
        **Evidence:** [1–2 sentence clear data-driven narrative supported by a specific metric or direct management statement.] 

        ## ⚖️ Regulatory Tailwinds
        **Assessment:** Strength: [🟢/🟡/🔴/⚫] | Direction: [✅/➖/❌]
        **Supporting Data:**
        - Addressable Subsidy/Tax Benefit Value: [$X value or N/A]
        - Regulatory Compliance Status: [Core policy metric if applicable]
        **Evidence:** [1–2 sentence clear data-driven narrative supported by a specific metric or direct management statement.] 

        ## 🤝 Strategic Partnerships & M&A
        **Assessment:** Strength: [🟢/🟡/🔴/⚫] | Direction: [✅/➖/❌]
        **Supporting Data:**
        - Transaction/Deal Capital Volume: [$X million or transaction count]
        - Acquired Revenue/Synergy Target: [$X value or projected impact]
        **Evidence:** [1–2 sentence clear data-driven narrative supported by a specific metric or direct management statement.] 

        ## ⚙️ Operational Efficiency
        **Assessment:** Strength: [🟢/🟡/🔴/⚫] | Direction: [✅/➖/❌]
        **Supporting Data:**
        - Gross/Operating Margin Expansion: [+X% YoY]
        - Cost Reduction Capital Saved: [$X million saved]
        **Evidence:** [1–2 sentence clear data-driven narrative supported by a specific metric or direct management statement.] 

        ## ⚠️ Risks & Final Considerations
        - **Primary Growth Risk:** [Identify and explain the most significant threat to the company's future growth profile, backed by a clear cited data point.]
        - **Competitive Landscape Overview:** [Brief narrative on market share dynamics or market fragmentation.]
        - **Valuation Risk context:** [Core growth valuation metrics like forward P/E or PEG ratio vs closest peers.]

        ## 🔗 Sources Used
        [1] [Exact name of primary filing or transcript used]
        [2] [Exact name of secondary source or analyst presentation used]
        """
        try:
            response = client.models.generate_content(model="gemini-2.5-flash", contents=growth_analysis_prompt, config=config)
            st.write(response.text)
        except Exception as e:
            st.error(f"Error running Business Growth Analysis: {e}")


    # ------------------------------------------------------------------
    # 🔴 PROMPT #4: Key Metrics Analysis Rev 2.2 (Optimised for your tool)
    # ------------------------------------------------------------------
    with st.expander("📊 Business Key Metrics Analysis", expanded=True):
        metrics_analysis_prompt = f"""
        CRITICAL OPERATIONAL INSTRUCTION: You are an expert financial analyst evaluating a company's phase-appropriate metrics using a strict Red/Yellow/Green framework. 
        Target Stock Ticker: '{ticker}'
        Target Corporate Phase: '{phase_num}'

        Step 1: Use your Google Search tool to identify today's current date and year.
        Step 2: Locate the most recent 10-K, 10-Q, Annual Reports, and institutional financial databases for ticker '{ticker}'.
        Step 3: Extract the necessary historical numbers (Revenue CAGR, Gross/Operating Margins, FCF, Dilution, ROIC) required to calculate the performance thresholds below.
        Step 4: Strictly calculate and map your findings to the thresholds specified below for the designated Target Corporate Phase:

        PHASE 1: STARTUP (Evaluate these exact metrics):
        - Product-Market Fit (via NPS): 🔴 0-10 | 🟡 10-19 | 🟢 >20
        - CAC Payback (Months): 🔴 >19 | 🟡 13-18 | 🟢 <12
        - Gross Margin Direction: 🔴 Declining/Erratic (>10pp variance QoQ) | 🟡 Stable (+/-1pp variance QoQ) | 🟢 Rising
        - Cash Burn Runway: 🔴 <2 years | 🟡 2-4 Years | 🟢 >4 years or FCF positive
        - Dilution 3yr CAGR: 🔴 >30% | 🟡 10-30% | 🟢 <10%

        PHASE 2: RAPID GROWTH (Evaluate these exact metrics):
        - Revenue Growth (YoY): 🔴 5%-10% | 🟡 10%-20% | 🟢 >20%
        - RULE OF 40 (Growth + EBITDA Margin): 🔴 <40% | 🟡 41-50% | 🟢 >50%
        - FCF Margin: 🔴 Negative | 🟡 0-5% | 🟢 >5%
        - Dilution TTM: 🔴 >10% | 🟡 5-10% | 🟢 <5%

        PHASE 3: SOLID GROWTH (Evaluate these exact metrics):
        - Revenue 3yr CAGR: 🔴 5%-10% | 🟡 10%-20% | 🟢 >20%
        - Earnings 3yr CAGR: 🔴 <20% | 🟡 21-40% | 🟢 >41%
        - Operating Margin Trend (QoQ): 🔴 Declining (<-5%) | 🟡 Flat (-2% to +2%) | 🟢 Rising (>3%)
        - ROIC: 🔴 <8% | 🟡 9%-15% | 🟢 >16%
        - FCF Margin: 🔴 <5% | 🟡 5-10% | 🟢 >10%

        PHASE 4: MATURITY (Evaluate these exact metrics):
        - Revenue 3yr CAGR: 🔴 0%-8% | 🟡 9%-20% | 🟢 >21%
        - Earnings CAGR: 🔴 <10% | 🟡 10-20% | 🟢 >20%
        - ROIC: 🔴 <8% | 🟡 9%-15% | 🟢 >16%
        - Operating Margin Trend (QoQ): 🔴 Declining (<-5%) | 🟡 Flat (-2% to +2%) | 🟢 Rising (>3%)
        - FCF Margin: 🔴 <10% | 🟡 10-20% | 🟢 >20%
        - FCF Yield: 🔴 <2% | 🟡 3-4% | 🟢 >5%
        - Dilution 3yr CAGR: 🔴 >5% | 🟡 2-5% | 🟢 <2%

        PHASE 5: DECLINE (Evaluate these exact metrics):
        - Revenue 3yr CAGR: 🔴 0%-5% | 🟡 5%-10% | 🟢 >10%
        - Earnings CAGR: 🔴 <10% | 🟡 10-20% | 🟢 >20%
        - ROIC: 🔴 <10% | 🟡 10%-20% | 🟢 >20%
        - FCF Margin: 🔴 <20% | 🟡 20-30% | 🟢 >30%
        - Dilution 3yr CAGR: 🔴 >1% | 🟡 0% to -5% | 🟢 -5% to -10%

        Step 5: Generate your output using the exact template below. Do not add any conversational remarks, introductions, or extra explanations. Output ONLY the completed template:

        **Primary Phase:** [Insert phase classification here based on Phase Number requested]
        **Secondary Phase (if applicable):** [Optional]
        **Summary:** [Provide a clear, non-jargon, one-paragraph summary of the results written for a new investor.]

        | Metric Found | Actual Calculated Value | Benchmark Status (🔴/🟡/🟢) |
        | :--- | :--- | :--- |
        | [Insert Phase Metric 1 Name] | [X% or $X] | [🔴/🟡/🟢] |
        | [Insert Phase Metric 2 Name] | [X% or $X] | [🔴/🟡/🟢] |
        | [Insert Phase Metric 3 Name] | [X% or $X] | [🔴/🟡/🟢] |
        | [Insert Phase Metric 4 Name] | [X% or $X] | [🔴/🟡/🟢] |
        | [Insert Phase Metric 5 Name] | [X% or $X] | [🔴/🟡/🟢] |

        **Overall Scoring Rating:** [Provide the computed consensus rating, e.g., Mixed/Yellow or Highly Positive/Green]

        ## 🔗 Sources Used
        [1] [Exact name of core filing, statement, or transcript used]
        [2] [Exact name of auxiliary data engine used]
        """
        try:
            # We add phase_num directly to user contents so the prompt loop dynamically isolates the phase rules
            response = client.models.generate_content(
                model="gemini-2.5-flash", 
                contents=metrics_analysis_prompt, 
                config=config
            )
            st.write(response.text)
        except Exception as e:
            st.error(f"Error running Key Metrics Analysis: {e}")


    # ------------------------------------------------------------------
    # 🔴 PROMPT #5: Business Risk Analysis v2.0 (Optimized for your tool)
    # ------------------------------------------------------------------
    with st.expander("⚠️ Business Risk Analysis v2.0", expanded=True):
        risk_analysis_prompt = f"""
        CRITICAL OPERATIONAL INSTRUCTION: You are an expert risk analyst specializing in identifying and evaluating operational and strategic risks from corporate financial filings. Your target stock ticker is: '{ticker}'.

        Step 1: Use your Google Search tool to identify today's current date and year.
        Step 2: Search SEC EDGAR and official Company Investor Relations pages to locate the most recent 10-K (Item 1A Risk Factors, MD&A, Business Overview) and recent 10-Q filings for ticker '{ticker}'.
        Step 3: Evaluate the company strictly across the following four critical risk dimensions using the definitions below:
        
        1. Concentration Risk:
           - 🔴 Red: Few customers account for >20% of total revenue.
           - 🟡 Yellow: Largest single customer accounts for >15% of revenue.
           - 🟢 Green: Highly diversified customer base.
        2. Disruption Risk:
           - 🔴 Red: Clear, identifiable active disruption threat to core product lines.
           - 🟡 Yellow: Normal, manageable industry evolution or standard technology cycles.
           - 🟢 Green: The company itself is the dominant industry disruptor.
        3. Outside Forces Risk (Macro/Regulation/Commodities):
           - 🔴 Red: Extreme financial exposure to swift regulatory, political, commodity, or interest rate movements.
           - 🟡 Yellow: Normal operational exposure to macroeconomic trends.
           - 🟢 Green: Minimal exposure or naturally insulated business model.
        4. Competition Risk:
           - 🔴 Red: Severe pricing pressure, margin deterioration, or hyper-fragmented market.
           - 🟡 Yellow: Standard competitive environment with stable market shares.
           - 🟢 Green: Monopoly, duopoly, or dominant niche pricing power dynamics.

        Step 4: Calculate the Overall Summary Risk Level via a strict weighted score equation:
        Assign: Red = 5 points, Yellow = 2 points, Green = 1 point. 
        Add the score of all 4 pillars and divide by 4. 
        - If Average is 2.5 or higher -> High Risk 🔴
        - If Average is 1.5 to 2.4 -> Medium Risk 🟡
        - If Average is less than 1.5 -> Low Risk 🟢

        Step 5: Generate your output using the exact template below. Use bullet points for evidence instead of dense paragraphs, include trend arrows, and cite filing sections inline. Output ONLY the completed template:

        # ⚠️ Execution Risk Analysis: [Company Name] ({ticker})
        *Analyzing open-bracket [Company Name] using the most recent 10-K and 10-Q filings*

        ## 📊 Overall Summary
        - **Overall Risk Level:** [High Risk 🔴 / Medium Risk 🟡 / Low Risk 🟢] (Based on calculated score of [Insert Calculated Average numerical score])
        - **⚠️ Primary Risk Factors:** [List the 1-2 highest risk pillars identified]
        - **🛡️ Key Mitigation:** [Highlight the company's strongest corporate defensive asset or program mentioned in filings]

        ---

        ## 🎯 RISK ASSESSMENT DETAILS

        ### 🥚🧺 Concentration
        - **Rating:** [🔴Red / 🟡Yellow / 🟢Green] | **Trend:** [⬆️ Increasing Risk / ➖ Stable / ⬇️ Decreasing Risk]
        - **Evidence:** [Provide 1-2 concise bullet points with hard metrics and inline filing section citations]
        - **Mitigation:** [Summarize the company's defensive strategy to diversify or manage this exposure]

        ### 🥷 Disruption
        - **Rating:** [🔴Red / 🟡Yellow / 🟢Green] | **Trend:** [⬆️ Increasing Risk / ➖ Stable / ⬇️ Decreasing Risk]
        - **Evidence:** [Provide 1-2 concise bullet points with hard metrics and inline filing section citations]
        - **Mitigation:** [Summarize the company's R&D or adaptive execution strategy to address disruption]

        ### 🕵️ Outside Forces
        - **Rating:** [🔴Red / 🟡Yellow / 🟢Green] | **Trend:** [⬆️ Increasing Risk / ➖ Stable / ⬇️ Decreasing Risk]
        - **Evidence:** [Provide 1-2 concise bullet points with hard metrics and inline filing section citations]
        - **Mitigation:** [Summarize corporate hedging, policy advocacy, or structural adaptations used to blunt outside impacts]

        ### 👥 Competition
        - **Rating:** [🔴Red / 🟡Yellow / 🟢Green] | **Trend:** [⬆️ Increasing Risk / ➖ Stable / ⬇️ Decreasing Risk]
        - **Evidence:** [Provide 1-2 concise bullet points with hard metrics and inline filing section citations]
        - **Mitigation:** [Summarize how the company maintains its pricing power, brand, or cost efficiencies to win]

        ## 🔗 Sources Used
        [1] [Exact name and section of primary 10-K filing used]
        [2] [Exact name and section of primary 10-Q filing used]
        """
        try:
            response = client.models.generate_content(model="gemini-2.5-flash", contents=risk_analysis_prompt, config=config)
            st.write(response.text)
        except Exception as e:
            st.error(f"Error running Business Risk Analysis: {e}")


    # ------------------------------------------------------------------
    # 🔴 PROMPT #6: Financial Statement Analysis v1.1 (Text-Only Edition)
    # ------------------------------------------------------------------
    with st.expander("📊 Financial Statement Analysis v1.1", expanded=True):
        financial_analysis_prompt = f"""
        CRITICAL OPERATIONAL INSTRUCTION: You are an expert financial analyst specializing in evaluating corporate financial health using ONLY official 10-K and 10-Q statements. Your target stock ticker is: '{ticker}'.

        Step 1: Identify today's current year by establishing a baseline via a web search if necessary. 
        Step 2: Access official SEC EDGAR data at www.sec.gov or official Investor Relations portals to extract the most recent 10-K and 10-Q financial statements for ticker '{ticker}'. (Strictly avoid third-party financial databases or aggregators).
        Step 3: Evaluate the data across the specified Income Statement, Balance Sheet, and Cash Flow metrics, comparing them against the same period last year. Score each individual check as 🔴 (Weak/Negative Trend), 🟡 (Stable/Flat Trend), or 🟢 (Strong/Positive Trend).
        Step 4: Separately calculate the section summary averages for the Income Statement, Balance Sheet, and Cash Flow metrics based on your individual scores.

        Step 5: Generate your output using the exact template below. Do not add any conversational remarks, introductions, or extra explanations. Output ONLY the completed template:

        # 📊 Financial Health Analysis: [Company Name] ({ticker})
        *Analyzing open-bracket [Company Name] using 10-K from [date] and 10-Q from [quarter]*

        ## ✅ Overall Summary
        - **Overall Financial Health:** [Strong / Moderate / Weak]
        - **Key Positive Indicators:** [List top 2-3 specific financial strengths]
        - **Key Concerns:** [List top 2-3 specific balance sheet or trend weaknesses]

        ---

        ## 🔍 Detailed Analysis 

        ### 📋 Income Statement
        - **Revenue Trend:** [⬆️/➖/⬇️] | **Score:** [🔴/🟡/🟢] | *Evidence:* [Provide brief metric evidence with inline filing section citation]
        - **Gross Profit Trend:** [⬆️/➖/⬇️] | **Score:** [🔴/🟡/🟢] | *Evidence:* [...]
        - **Operating Income Trend:** [⬆️/➖/⬇️] | **Score:** [🔴/🟡/🟢] | *Evidence:* [...]
        - **EPS Trend:** [⬆️/➖/⬇️] | **Score:** [🔴/🟡/🟢] | *Evidence:* [...]
        - **Dilution & SBC Stability:** [⬆️/➖/⬇️] | **Score:** [🔴/🟡/🟢] | *Evidence:* [...]
        - **Summary Score (Income Statement):** [🔴 / 🟡 / 🟢]

        ### 🏦 Balance Sheet
        - **Cash & Securities:** [⬆️/➖/⬇️] | **Score:** [🔴/🟡/🟢] | *Evidence:* [...]
        - **Debt Levels:** [⬆️/➖/⬇️] | **Score:** [🔴/🟡/🟢] | *Evidence:* [...]
        - **Retained Earnings:** [⬆️/➖/⬇️] | **Score:** [🔴/🟡/🟢] | *Evidence:* [...]
        - **Stock Repurchases:** [⬆️/➖/⬇️] | **Score:** [🔴/🟡/🟢] | *Evidence:* [...]
        - **Summary Score (Balance Sheet):** [🔴 / 🟡 / 🟢]

        ### 💸 Cash Flows
        - **Free Cash Flow:** [⬆️/➖/⬇️] | **Score:** [🔴/🟡/🟢] | *Evidence:* [...]
        - **Operating Cash Flow:** [⬆️/➖/⬇️] | **Score:** [🔴/🟡/🟢] | *Evidence:* [...]
        - **CapEx Trends:** [⬆️/➖/⬇️] | **Score:** [🔴/🟡/🟢] | *Evidence:* [...]
        - **Margin Profiles (Gross/Operating):** [⬆️/➖/⬇️] | **Score:** [🔴/🟡/🟢] | *Evidence:* [...]
        - **Summary Score (Cash Flow):** [🔴 / 🟡 / 🟢]

        ## 🔗 Sources Used
        [1] [Exact URL text or filing identifier from www.sec.gov]
        [2] [Official Company Investor Relations report identifier]
        """

        try:
            response = client.models.generate_content(model="gemini-2.5-flash", contents=financial_analysis_prompt, config=config)
            st.markdown(response.text)
        except Exception as e:
            st.error(f"Error executing Financial Statement Analysis: {e}")


    # ------------------------------------------------------------------
    # 🔴 PROMPT #7: Business Valuation Analysis (Optimized for your tool)
    # ------------------------------------------------------------------
    with st.expander("💰 Business Valuation Analysis", expanded=True):
        valuation_analysis_prompt = f"""
        CRITICAL OPERATIONAL INSTRUCTION: You are an expert equity analyst applying the appropriate valuation methodology for a company's specific lifecycle business phase using a strict benchmarking framework.
        Target Stock Ticker: '{ticker}'
        Target Corporate Phase: '{phase_num}'

        Step 1: Use your Google Search tool to identify today's current date and year.
        Step 2: Search SEC EDGAR data at www.sec.gov or official international Investor Relations portals to locate the most recent 10-K, 10-Q, Annual Reports, and official earnings transcripts for ticker '{ticker}'.
        Step 3: Extract the necessary valuation metrics (Share price, fully diluted share count, cash, total debt, revenue trends, operating income, and available management guidance/consensus expectations).
        Step 4: Execute the valuation calculations strictly aligned to the designated Phase Number instruction below:
        
        - PHASE 1: STARTUP -> Primary: Forward P/S | Secondary: Price/Gross Profit (P/GP)
        - PHASE 2: RAPID GROWTH -> Primary: EV/Sales | Secondary: Forward P/S
        - PHASE 3: SOLID GROWTH -> Primary: Price-to-Sales (P/S) | Secondary: Forward EV/EBITDA
        - PHASE 4: MATURITY -> Primary: Discounted Cash Flow (DCF) or Reverse DCF | Secondary: Forward P/E
        - PHASE 5: DECLINING -> Primary: Sum-of-the-Parts (SOTP) / Net Asset Value (NAV) | Secondary: Dividend Yield vs ERP

        *Industry Override Rule:* If the target company operates in Biotech/Life Sciences, prioritize a probability-adjusted NPV (pNPV). If SaaS, anchor using the Rule of 40 and EV/Gross Profit. If Energy/Mining, prioritize NAV/EV per Reserves. If a Bitcoin/Crypto Treasury, check mNAV vs peers.

        Step 5: Apply peer group multi-comparison or the company's historical 3-year trailing range to assign a strict benchmarking status score:
        - 🟩 Green = Undervalued (Multiple ≤ peer 25th percentile OR ≤ company's own 3-year low range)
        - 🟨 Yellow = Fairly Valued / Within normal range (Multiple between the peer 25th and 75th percentiles)
        - 🟥 Red = Overvalued (Multiple ≥ peer 75th percentile OR ≥ company's own 3-year high range)

        Step 6: Generate your output using the exact template below. Do not add any conversational introductions, greetings, or extra explanations. Output ONLY the completed template:

        **Company:** [Company Name / Ticker]
        **Phase:** [{phase_num}] - [Insert matching phase taxonomy title name]
        **Summary:** [Select one: 🟩 Undervalued / 🟨 Fairly Valued / 🟥 Overvalued]  

        ### 📐 Core Valuation Metrics Summary Table
        | Metric Computed | Valuation Formula Used | Target Corporate Metric Value | Peer / Historical Benchmark Status |
        | :--- | :--- | :--- | :--- |
        | [Primary Method Name] | [Insert Formula Definition] | [Calculated Value, e.g., 4.2x] | [🟩 Green / 🟨 Yellow / 🟥 Red] |
        | [Secondary Method Name] | [Insert Formula Definition] | [Calculated Value, e.g., 12.5x] | [🟩 Green / 🟨 Yellow / 🟥 Red] |

        - **Key Valuation Drivers:** [Provide a concise, 1-2 sentence scannable summary detailing how top-line growth, operating margins, or core structural risks are driving this specific multiple pricing.]
        - **Sensitivity & Margin of Safety:** [Explain the fundamental corporate assumptions—such as changes in cost of capital, regulatory outcomes, or guidance misses—that would immediately shift this valuation footprint.]

        ## 🔗 Sources Used
        [1] [Exact name of core primary SEC filing or IR financial report used]
        [2] [Exact name of transcript or secondary market data database utilized]
        """
        try:
            response = client.models.generate_content(model="gemini-2.5-flash", contents=valuation_analysis_prompt, config=config)
            st.markdown(response.text)
        except Exception as e:
            st.error(f"Error executing Business Valuation Analysis: {e}")


    # ------------------------------------------------------------------
    # 🔴 PROMPT #8: Intrinsic Valuation Analysis V1 (Optimized for your tool)
    # ------------------------------------------------------------------
    with st.expander("🧬 Intrinsic Valuation Analysis V1", expanded=True):
        intrinsic_valuation_prompt = f"""
        CRITICAL OPERATIONAL INSTRUCTION: You are an expert equity analyst executing a rigorous intrinsic valuation protocol matched mechanically to a company's business cycle phase.
        Target Stock Ticker: '{ticker}'
        Target Corporate Phase: '{phase_num}'

        Step 1: Use your Google Search tool to identify today's current date and year.
        Step 2: Search SEC EDGAR (www.sec.gov) or international Investor Relations portals to acquire the latest 10-K, 10-Q, annual accounts, and earnings call transcripts for ticker '{ticker}'.
        Step 3: Extract core quantitative baseline metrics: TTM revenue, 3-year history, historical operating margins, share count, long-term consensus guidance, cash, total debt, interest expense, and the effective tax rate.
        Step 4: Dynamically calculate the Weighted Average Cost of Capital (WACC) to serve as your core discount rate using the strict mathematical expression:
        $$WACC = \\frac{{E}}{{V}} \\times r_e + \\frac{{D}}{{V}} \\times r_d \\times (1 - T)$$
        Where: E = Market value of equity, D = Market value of debt, V = E + D, re = Cost of equity via CAPM, rd = Cost of debt, T = Corporate tax rate.

        Step 5: Compute the intrinsic company value applying the exact Phase Taxonomy method below:
        - Phase 1: Startup -> DCF with Scenario Analysis paired with the Venture Capital (VC) Method.
        - Phase 2: Early Growth -> Multi-Stage DCF (Aggressive Growth to Transition) cross-referenced with EV/EBITDA multiples.
        - Phase 3: Solid Growth -> Two-Stage DCF model or a Residual Income Model.
        - Phase 4: Maturity -> Single-Stage DCF or Dividend Discount Model (DDM).
        - Phase 5: Decline -> Adjusted Present Value (APV) or a strict asset Liquidation Value analysis.

        Step 6: Generate your output using the exact template below. Do not add any conversational remarks, intros, or extra explanations. Output ONLY the completed template:

        **Company Name:** [Company Name] 
        **Business Phase:** [{phase_num}] - [Insert matching phase taxonomy name] 

        ### 📊 Valuation Summary
        - **Method Used:** [Identify the primary and cross-reference validation methods applied]
        - **Justification:** [Provide a brief 1-2 sentence overview explaining why this mechanical selection fits the asset's current phase profile.]

        ### ⚙️ Key Valuation Assumptions
        - **Projected Revenue Growth (CAGR):** [X%]
        - **Target Operating Margin:** [X%]
        - **Calculated WACC:** [X%]
        - **Terminal Growth Rate:** [X%]

        ### 🧮 Intrinsic Value Calculation
        #### Step-by-Step Execution Breakdown:
        1. **Baseline Inflows / Multiples Projection:** [Show the explicit mathematical steps, terminal values, or scenario weights generated from the primary model inputs.]
        2. **Discounting / Present Value Summation:** [Show the cash flows or values being discounted back to today's dollar terms using your WACC rate or phase parameters.]
        3. **Per-Share Derivation:** [Deduct net debt positions if calculating enterprise values, and divide the target balance by the fully diluted shares outstanding count.]

        #### Core Valuation Output Findings:
        - **Final Intrinsic Value:** [Currency and Amount, e.g., USD 142.50]
        - **Current Market Price:** [Currency and Amount, e.g., USD 120.00] 
        - **Price Difference / Margin of Safety:** [State whether the asset is Undervalued or Overvalued, and by what percentage relative to its intrinsic value score.]

        ## 🔗 Sources Used
        [1] [Exact file name and identifier from www.sec.gov or primary data engine]
        [2] [Official Company Investor Relations corporate transcript or presentation reference]
        """
        try:
            response = client.models.generate_content(model="gemini-2.5-flash", contents=intrinsic_valuation_prompt, config=config)
            st.markdown(response.text)
        except Exception as e:
            st.error(f"Error executing Intrinsic Valuation Analysis: {e}")
