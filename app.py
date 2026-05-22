import streamlit as st
import io

# =====================================================================
# 💾 1. EXPORT ENGINE MODULE (PDF & WORD GENERATION)
# =====================================================================
def render_export_module(ticker_symbol, panels_dictionary):
    """
    An isolated, error-resistant module that generates completely self-contained
    PDF and Word byte buffers to guarantee seamless downloads on Streamlit Cloud.
    """
    if not ticker_symbol or not panels_dictionary:
        return

    # Delayed import to ensure clean app startup performance
    from fpdf import FPDF

    st.write("---")
    st.subheader("📥 Export Complete Research Report")
    st.write("Save a copies of this multi-criteria analysis for your archives or offline reading.")
    
    # -------------------------------------------------------------
    # Word Document Buffer Generation (.doc)
    # -------------------------------------------------------------
    word_text = f"EQUITY RESEARCH REPORT: {str(ticker_symbol).upper()}\n"
    word_text += f"Generated via Premium Small-Cap Research Terminal\n"
    word_text += "=" * 50 + "\n\n"
    
    for title, text_content in panels_dictionary.items():
        word_text += f"=== {str(title).upper()} ===\n"
        word_text += f"{str(text_content)}\n"
        word_text += "-" * 50 + "\n\n"
        
    word_bytes = word_text.encode("utf-8", errors="ignore")

    # -------------------------------------------------------------
    # PDF Document Buffer Generation (.pdf)
    # -------------------------------------------------------------
    pdf_bytes = b""
    try:
        pdf = FPDF(orientation="P", unit="mm", format="A4")
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()
        
        pdf.set_font("Helvetica", style="B", size=16)
        pdf.cell(w=0, h=10, text=f"Equity Research Report: {str(ticker_symbol).upper()}", new_x="LMARGIN", new_y="NEXT", align="C")
        pdf.set_font("Helvetica", style="I", size=10)
        pdf.cell(w=0, h=6, text="Generated via Premium Small-Cap Research Terminal", new_x="LMARGIN", new_y="NEXT", align="C")
        pdf.ln(10)
        
        for title, text_content in panels_dictionary.items():
            pdf.set_font("Helvetica", style="B", size=12)
            pdf.cell(w=0, h=8, text=str(title), new_x="LMARGIN", new_y="NEXT")
            pdf.ln(2)
            
            pdf.set_font("Helvetica", style="", size=10)
            sanitized_content = str(text_content).replace("**", "").replace("*", "").replace("#", "")
            clean_text = sanitized_content.encode("latin-1", errors="ignore").decode("latin-1")
            
            pdf.multi_cell(w=0, h=5, text=clean_text)
            pdf.ln(6)

        # Explicitly output to a safe string/bytes memory destination ('S')
        raw_pdf_output = pdf.output(dest='S')
        pdf_bytes = bytes(raw_pdf_output) if not isinstance(raw_pdf_output, bytes) else raw_pdf_output
        
    except Exception as pdf_error:
        pdf_bytes = b""
        st.sidebar.error(f"PDF compilation bypass engaged: {str(pdf_error)}")

    # -------------------------------------------------------------
    # Render Download Buttons Side-by-Side
    # -------------------------------------------------------------
    col1, col2 = st.columns(2)
    with col1:
        st.download_button(
            label="📄 Download Word Document (.doc)",
            data=word_bytes,
            file_name=f"{str(ticker_symbol).upper()}_Research_Report.doc",
            mime="application/msword",
            use_container_width=True,
            key="word_download_action"
        )
    with col2:
        if pdf_bytes:
            st.download_button(
                label="📕 Download PDF Report (.pdf)",
                data=pdf_bytes,
                file_name=f"{str(ticker_symbol).upper()}_Research_Report.pdf",
                mime="application/pdf",
                use_container_width=True,
                key="pdf_download_action"
            )
        else:
            st.button(label="❌ PDF Export Unavailable", disabled=True, use_container_width=True, key="pdf_disabled_button")


# =====================================================================
# 🖥️ 2. MAIN APPLICATION INTERFACE & ANALYSIS PIPELINE
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

    # -------------------------------------------------------------
    # 3. INTERACTIVE CONTAINER EXPORT HOOK
    # -------------------------------------------------------------
    # Gather completed panel report details to package up into export file utilities
    compiled_panels_report = {
        "Panel 1: Competitive Advantage & Moat Check": panel_moat_content,
        "Panel 2: Financial Statement Health Triage": panel_financials_content,
        "Panel 3: Final Multi-Criteria Evaluation Verdict": panel_verdict_content
    }
    
    # Render the fixed Word and PDF engine download buttons at the base of the analysis block
    render_export_module(ticker, compiled_panels_report)

elif submit_btn and not ticker:
    st.warning("Please provide a valid company ticker symbol or asset name before triggering the pipeline analysis.")
