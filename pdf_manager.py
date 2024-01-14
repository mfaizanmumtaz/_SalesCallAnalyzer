import streamlit as st
from fpdf import FPDF
import tempfile

from fpdf import FPDF
import tempfile

def create_pdf(text):
    """Create a PDF with the given text and save to a temporary file."""
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    
    # Define the width for wrapping the text (width of the page minus margins)
    effective_page_width = pdf.w - 2*pdf.l_margin
    
    # Split the text into lines, wrapping the text to fit the page width
    pdf.multi_cell(effective_page_width, 6, text)
    
    # Save the PDF to a temporary file
    temp_pdf = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    pdf.output(temp_pdf.name)
    return temp_pdf


def download_pdf(user_input,file_name):
    temp_pdf = create_pdf(user_input)
    with open(temp_pdf.name, "rb") as file:
        st.download_button(
            label="Download In PDF",
            data=file,
            file_name=f"{file_name}.pdf",
            mime="application/pdf"
        )
    temp_pdf.close() 