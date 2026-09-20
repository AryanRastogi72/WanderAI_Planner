from fpdf import FPDF
import os

def generate_itinerary_pdf(markdown_text: str, filename: str = "itinerary.pdf"):
    """
    Generates a simple PDF from the agent's text response.
    It strips most markdown for simplicity, but keeps the structure clean.
    """
    
    # Define a custom PDF class that inherits from FPDF to add headers and footers
    class PDF(FPDF):
        def header(self):
            # Set font to Arial, bold, size 15 for the header
            self.set_font('Arial', 'B', 15)
            # Add a centered title
            self.cell(0, 10, 'WanderAI Travel Itinerary', 0, 1, 'C')
            # Add a line break
            self.ln(5)
            
        def footer(self):
            # Position at 15 mm from the bottom
            self.set_y(-15)
            # Set font to Arial, italic, size 8 for the page number
            self.set_font('Arial', 'I', 8)
            self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

    # Initialize the PDF and add the first page
    pdf = PDF()
    pdf.add_page()
    pdf.set_font("Arial", size=11)
    
    import textwrap
    
    # Very basic markdown cleaning (remove bold asterisks)
    clean_text = markdown_text.replace('**', '').replace('__', '')
    
    # Process the text line by line
    for line in clean_text.split('\n'):
        # Handle basic links by extracting just the text: [text](url) -> text
        import re
        line = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', line)
        
        # Ensure text is encoded properly for FPDF (latin-1)
        # We replace unencodable characters (like emojis) with '?' to prevent crashes
        safe_line = line.encode('latin-1', 'replace').decode('latin-1')
        
        # If the line is a Markdown header (starts with #)
        if safe_line.startswith('#'):
            pdf.set_font("Arial", 'B', 12)
            safe_line = safe_line.lstrip('#').strip()
            
            # Wrap long headers so they don't break the PDF boundaries
            for chunk in textwrap.wrap(safe_line, width=90):
                try:
                    pdf.multi_cell(0, 8, txt=chunk)
                except Exception:
                    pass
                    
            # Reset font back to normal size
            pdf.set_font("Arial", size=11)
            
        # If it's a normal line of text
        else:
            # Wrap normal lines (URLs can be very long and cause FPDF errors)
            for chunk in textwrap.wrap(safe_line, width=100):
                try:
                    pdf.multi_cell(0, 6, txt=chunk)
                except Exception:
                    pass
            
    # fpdf2 output() returns a bytearray by default. 
    # Streamlit requires a bytes object for the download button, so we convert it.
    try:
        pdf_output = bytes(pdf.output())
    except TypeError:
        # Fallback if an older version of fpdf (fpdf1) is used
        pdf_output = pdf.output(dest="S").encode("latin-1")
        
    return pdf_output
