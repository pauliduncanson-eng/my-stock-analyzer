import streamlit as st
import io
from fpdf import FPDF

def render_export_module(ticker_symbol, panels_dictionary):
    """
    An isolated, error-resistant module that generates completely self-contained
    PDF and Word byte buffers to guarantee seamless downloads on Streamlit Cloud.
    """
    # 🛑 SAFETY GATE 1: If no ticker or data exists yet, quietly exit the function
    # to prevent the app from breaking on initial page load.
    if not ticker_symbol or not panels_dictionary:
        return

    st.write("---")
    st.subheader("📥 Export Complete Research Report")
    st.write("Save a copy of this generation for your archives or offline reading.")
    
    # -------------------------------------------------------------
    # 1. PRE-GENERATE THE WORD DOCUMENT BUFFER (.doc)
    # -------------------------------------------------------------
    word_text = f"EQUITY RESEARCH REPORT: {str(ticker_symbol).upper()}\n"
    word_text += f"Generated via Research Terminal Platform\n"
    word_text += "=" * 40 + "\n\n"
    
    # 🛑 SAFETY GATE 2: Handle cases where panels_dictionary might be a string or corrupted
    if isinstance(panels_dictionary, dict):
        for title, text_content in panels_dictionary.items():
            word_text += f"=== {str(title).upper()} ===\n"
            word_text += f"{str(text_content)}\n"
            word_text += "-" * 40 + "\n\n"
    else:
        # Fallback if raw text was passed instead of a dictionary
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

        pdf_bytes = pdf.output()
        
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
