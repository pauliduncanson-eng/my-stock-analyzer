import streamlit as st
import io
from fpdf import FPDF

def render_export_module(ticker_symbol, panels_dictionary):
    """
    An isolated, error-resistant module that generates completely self-contained
    PDF and Word byte buffers to guarantee seamless downloads on Streamlit Cloud.
    
    :param ticker_symbol: String (e.g., 'AAPL', 'MSFT')
    :param panels_dictionary: Dict where keys are panel titles and values are raw string outputs
    """
    st.write("---")
    st.subheader("📥 Export Complete Research Report")
    st.write("Save a copy of this generation for your archives or offline reading.")
    
    # -------------------------------------------------------------
    # 1. PRE-GENERATE THE WORD DOCUMENT BUFFER (.doc)
    # -------------------------------------------------------------
    # We construct a clean text document featuring explicit structural separation
    word_text = f"EQUITY RESEARCH REPORT: {ticker_symbol.upper()}\n"
    word_text += f"Generated via Research Terminal Platform\n"
    word_text += "=" * 40 + "\n\n"
    
    for title, text_content in panels_dictionary.items():
        word_text += f"=== {title.upper()} ===\n"
        word_text += f"{text_content}\n"
        word_text += "-" * 40 + "\n\n"
        
    # Convert string directly to clean, system-agnostic bytes
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
        pdf.cell(w=0, h=10, text=f"Equity Research Report: {ticker_symbol.upper()}", new_x="LMARGIN", new_y="NEXT", align="C")
        pdf.set_font("Helvetica", style="I", size=10)
        pdf.cell(w=0, h=6, text="Generated via Research Terminal Engine", new_x="LMARGIN", new_y="NEXT", align="C")
        pdf.ln(10)
        
        for title, text_content in panels_dictionary.items():
            # Section Title Block
            pdf.set_font("Helvetica", style="B", size=12)
            pdf.cell(w=0, h=8, text=title, new_x="LMARGIN", new_y="NEXT")
            pdf.ln(2)
            
            # Content Paragraph Sanitization & Formatting
            pdf.set_font("Helvetica", style="", size=10)
            
            # Strip out markdown symbols (*, #) that ruin PDF plaintext layouts
            sanitized_content = text_content.replace("**", "").replace("*", "").replace("#", "")
            
            # Convert unicode safely to latin-1 parameters to prevent high-byte crashes
            clean_text = sanitized_content.encode("latin-1", errors="ignore").decode("latin-1")
            
            # Use multi_cell to handle line wrapping naturally
            pdf.multi_cell(w=0, h=5, text=clean_text)
            pdf.ln(6)
            
        # Compile into raw binary byte array format natively
        pdf_bytes = pdf.output()
        
    except Exception as pdf_error:
        # Graceful fallback indicator so the UI never locks up or crashes out
        pdf_bytes = b""
        st.sidebar.error(f"PDF compilation bypass engaged: {str(pdf_error)}")


    # -------------------------------------------------------------
    # 3. RENDER THE MEMORY-BOUND DOWNLOAD BUTTONS SIDE-BY-SIDE
    # -------------------------------------------------------------
    col1, col2 = st.columns(2)
    
    with col1:
        st.download_button(
            label="📄 Download Word Document (.doc)",
            data=word_bytes,
            file_name=f"{ticker_symbol.upper()}_Research_Report.doc",
            mime="application/msword",
            use_container_width=True,
            key="word_download_action"
        )
        
    with col2:
        if pdf_bytes:
            st.download_button(
                label="📕 Download PDF Report (.pdf)",
                data=pdf_bytes,
                file_name=f"{ticker_symbol.upper()}_Research_Report.pdf",
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
