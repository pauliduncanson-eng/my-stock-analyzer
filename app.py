import streamlit as st
import io

# =====================================================================
# 💾 EXPORT MODULE (PDF & WORD ENGINE)
# =====================================================================
def render_export_module(ticker_symbol, panels_dictionary):
    """
    An isolated, error-resistant module that generates completely self-contained
    PDF and Word byte buffers to guarantee seamless downloads on Streamlit Cloud.
    """
    # 🛑 SAFETY GATE 1: If no ticker or data exists yet, quietly exit the function
    # to prevent the app from breaking on initial page load.
    if not ticker_symbol or not panels_dictionary:
        return

    # 🩹 DELAYED IMPORT: Move this inside the function to keep app startup clean
    from fpdf import FPDF

    st.write("---")
    st.subheader("📥 Export Complete Research Report")
    st.write("Save a copy of this generation for your archives or offline reading.")
    
    # -------------------------------------------------------------
    # 1. PRE-GENERATE THE WORD DOCUMENT BUFFER (.doc)
    # -------------------------------------------------------------
    word_text = f"EQUITY RESEARCH REPORT: {str(ticker_symbol).upper()}\n"
    word_text += f"Generated via Research Terminal Platform\n"
    word_text += "=" * 40 + "\n\n"
    
    if isinstance(panels_dictionary, dict):
        for title, text_content in panels_dictionary.items():
            word_text += f"=== {str(title).upper()} ===\n"
            word_text += f"{str(text_content)}\n"
            word_text += "-" * 40 + "\n\n"
    else:
        word_text += f"{str(panels_dictionary)}\n"
        
    word_bytes = word_text.encode("utf-8", errors="ignore")

    # -------------------------------------------------------------
    # 2. PRE-GENERATE THE PDF DOCUMENT BUFFER (.pdf)
    # -------------------------------------------------------------
    pdf_bytes = b""
    try:
        pdf = FPDF(orientation="P", unit="mm", format="A4")
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()
        
        # Document Main Header Style
        pdf.set_font("Helvetica", style="B", size=16)
        pdf.cell(w=0, h=10, text=f"Equity Research Report: {str(ticker_symbol).upper()}", new_x="LMARGIN", new_y="NEXT", align="C")
        pdf.set_font("Helvetica", style="I", size=10)
        pdf.cell(w=0, h=6, text="Generated via Research Terminal Engine", new_x="LMARGIN", new_y="NEXT", align="C")
        pdf.ln(10)
        
        if isinstance(panels_dictionary, dict):
            for title, text_content in panels_dictionary.items():
                # Section Title Block
                pdf.set_font("Helvetica", style="B", size=12)
                pdf.cell(w=0, h=8, text=str(title), new_x="LMARGIN", new_y="NEXT")
                pdf.ln(2)
                
                # Content Paragraph Sanitization & Formatting
                pdf.set_font("Helvetica", style="", size=10)
                sanitized_content = str(text_content).replace("**", "").replace("*", "").replace("#", "")
                clean_text = sanitized_content.encode("latin-1", errors="ignore").decode("latin-1")
                
                pdf.multi_cell(w=0, h=5, text=clean_text)
                pdf.ln(6)
        else:
            pdf.set_font("Helvetica", style="", size=10)
            sanitized_content = str(panels_dictionary).replace("**", "").replace("*", "").replace("#", "")
            clean_text = sanitized_content.encode("latin-1", errors="ignore").decode("latin-1")
            pdf.multi_cell(w=0, h=5, text=clean_text)

        # 🔧 FIX: Explicitly output to a safe string/bytes destination ('S')
        raw_pdf_output = pdf.output(dest='S')
        
        # Ensure it's explicitly cast to a bytes object for st.download_button
        pdf_bytes = bytes(raw_pdf_output) if not isinstance(raw_pdf_output, bytes) else raw_pdf_output
        
    except Exception as pdf_error:
        pdf_bytes = b""
        st.sidebar.error(f"PDF compilation bypass engaged: {str(pdf_error)}")

    # -------------------------------------------------------------
    # 3. RENDER THE DOWNLOAD BUTTONS SIDE-BY-SIDE
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
            st.button(
                label="❌ PDF Export Unavailable", 
                disabled=True, 
                use_container_width=True,
                key="pdf_disabled_button"
            )

# =====================================================================
# 🖥️ MAIN APPLICATION INTERFACE (YOUR EXISTING APPLICATION LOGIC)
# =====================================================================

st.title("🔎 Premium Small-Cap Research Terminal")
st.write("Enter a ticker symbol below to generate an end-to-end multi-panel research report.")

# Input Field for Ticker
ticker_input = st.text_input("Ticker Symbol (e.g., Schneider, Archos, Robot):", "").strip()

# --- Example of compiling data from your various research panels ---
# (Replace this sample block with your actual AI generation engine values)
if ticker_input:
    st.success(f"Analysis complete for: {ticker_input.upper()}")
    
    # This dictionary gathers your text sections to feed into the download buttons
    compiled_panels_data = {
        "Panel 1: Competitive Advantage & Moat": "Sample analysis regarding business competitive structural dynamics.",
        "Panel 5: Financial Health Check": "Sample overview of balance sheet allocations and free cash flow generation metric targets.",
        "Panel 8: Final Valuation Triage Verdict": "Sample final valuation scoring outcome verdict metric parameters."
    }
    
    # 🚀 CALL THE EXPORT UTILITY BUTTONS HERE
    render_export_module(ticker_input, compiled_panels_data)
