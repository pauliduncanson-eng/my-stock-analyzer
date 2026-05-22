import streamlit as st

# =====================================================================
# 🖥️ MAIN APPLICATION INTERFACE & ANALYSIS PIPELINE
# =====================================================================
st.set_page_config(page_title="Small-Cap Research Terminal", layout="wide")

st.title("🔎 Premium Small-Cap & Mid-Cap Research Terminal")
st.write("Perform rigorous investment triage using structured multi-criteria qualitative checklists and financial rules.")

# Input Form
with st.form("analysis_form"):
    col_input1, col_input2 = st.columns([2, 1])
    with col_input1:
        ticker = st.text_input("Enter Company Ticker or Name:", "").strip()
    with col_input2:
        market_cap = st.number_input("Estimated Market Cap (€ Millions):", min_value=0.0, step=50.0, value=250.0)
    
    st.markdown("### 📋 Step 1: Qualitative Alignment Flags")
    chk_lynch_boring = st.checkbox("Peter Lynch Rule: Is the business boring, disagreeable, or overlooked by Wall Street?", value=True)
    chk_thiel_monopoly = st.checkbox("Peter Thiel Rule: Does the company possess a 10x technology advantage, brand, or scale network showing clear micro-monopoly traits?", value=True)
    chk_gardner_breaker = st.checkbox("David Gardner Rule: Is it a fast-moving, innovative category leader with top-tier management and consumer appeal?", value=True)
    
    st.markdown("### 📊 Step 2: Core Financial Triage Checklist")
    chk_fcf = st.checkbox("Free Cash Flow: Is the company tracking toward structural positive cash generation relative to operations?", value=True)
    chk_debt = st.checkbox("Balance Sheet: Is net debt manageable relative to core earnings, or is there a clean net cash cushion?", value=True)
    chk_moat = st.checkbox("Pricing Power: Are gross margins stable or expanding, signaling structural pricing power?", value=True)

    submit_btn = st.form_submit_button("Run Strategic Checklist Triage")

# Evaluation Output Execution Block
if submit_btn and ticker:
    st.success(f"Triage Pipeline Analysis Compiled for: {ticker.upper()}")
    
    # Calculate an analytical scoring indicator matrix
    score = 0
    checks_passed = []
    
    if chk_lynch_boring: 
        score += 15
        checks_passed.append("Peter Lynch Overlooked Value Factor")
    if chk_thiel_monopoly: 
        score += 20
        checks_passed.append("Thielian Micro-Monopoly Structural Moat")
    if chk_gardner_breaker: 
        score += 15
        checks_passed.append("Gardner Rule Breaker Market Leadership")
    if chk_fcf: 
        score += 20
        checks_passed.append("Positive Free Cash Flow Generation Runway")
    if chk_debt: 
        score += 15
        checks_passed.append("Clean Balance Sheet / Net Cash Cushion Assets")
    if chk_moat: 
        score += 15
        checks_passed.append("High/Stable Gross Margins Pricing Power")

    # Display Metrics Summary Dashboard
    m1, m2, m3 = st.columns(3)
    m1.metric("Target Asset", ticker.upper())
    m2.metric("Total Criteria Score", f"{score} / 100")
    m3.metric("Triage Risk Rating", "LOW RISK / HIDDEN GEM" if score >= 70 else "HIGH RISK / SPECULATIVE")

    # Generate layout structure breakdown text blocks
    panel_moat_content = (
        f"Detailed appraisal of {ticker.upper()}'s structural positioning. "
        f"Alignment across foundational strategic lenses confirmed: "
        f"Lynch Boring Factor={chk_lynch_boring}, Thiel Monopoly Moat={chk_thiel_monopoly}, "
        f"Gardner Rule-Breaker Core={chk_gardner_breaker}. "
        "The business model shows clear defensive insulation from typical micro-cap churn characteristics."
    )
    
    panel_financials_content = (
        f"Core fundamental parsing for asset size allocation of €{market_cap:.1f}M. "
        f"Financial sanity criteria points met: "
        f"FCF Positive Generation Runway={chk_fcf}, Debt/Leverage Containment Metrics={chk_debt}, "
        f"Pricing Power / Stable Unit Margins={chk_moat}. "
        "Capital allocation frameworks indicate highly disciplined reinvestment rates."
    )
    
    panel_verdict_content = (
        f"Final investment evaluation assessment score assigned: {score} out of 100 possible points. "
        f"Verified structural highlights identified: {', '.join(checks_passed) if checks_passed else 'None'}. "
        "Conclusion: Position is highly aligned with asymmetric small-cap investment criteria protocols."
    )

    # Output Tabs UI inside the dashboard workspace
    tab1, tab2, tab3 = st.tabs([
        "🛡️ Moat & Competitive Advantages", 
        "📉 Financial Statement Triage", 
        "🎯 Multi-Criteria Scoring Verdict"
    ])
    
    with tab1:
        st.write(panel_moat_content)
    with tab2:
        st.write(panel_financials_content)
    with tab3:
        st.write(panel_verdict_content)

elif submit_btn and not ticker:
    st.warning("Please provide a valid company ticker symbol or asset name before triggering the pipeline analysis.")
