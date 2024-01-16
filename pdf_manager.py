import streamlit as st
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import pagesizes
import tempfile

def create_pdf(text):
    # Create a temporary file
    temp_pdf = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")

    # Create a canvas linked to the temporary file
    c = canvas.Canvas(temp_pdf.name, pagesize=letter)
    width, height = letter

    # Set up basic parameters
    font_name = "Helvetica"
    font_size = 12
    line_height = 14
    margin = 72
    x = margin
    y = height - margin
    max_width = width - 2 * margin

    c.setFont(font_name, font_size)

    # Function to wrap text
    def wrap_text(text, max_width):
        lines = []
        for paragraph in text.split('\n'):
            line = []
            width = 0
            for word in paragraph.split():
                word_width = c.stringWidth(word, font_name, font_size)
                if width + word_width <= max_width:
                    line.append(word)
                    width += word_width + c.stringWidth(' ', font_name, font_size)
                else:
                    lines.append(' '.join(line))
                    line = [word]
                    width = word_width
            lines.append(' '.join(line))
        return lines

    # Wrap and draw each line
    for line in wrap_text(text, max_width):
        c.drawString(x, y, line)
        y -= line_height
        if y < margin:
            c.showPage()
            c.setFont(font_name, font_size)
            y = height - margin

    # Save the PDF
    c.save()

    # Return the path to the temporary file
    return temp_pdf

def download_pdf(user_input,file_name):
    temp_pdf = create_pdf(user_input)
    with open(temp_pdf.name, "rb") as file:
        st.download_button(
            label="Download As PDF",
            data=file,
            file_name=f"{file_name}.pdf",
            mime="application/pdf"
        )
    temp_pdf.close()