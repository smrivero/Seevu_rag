from fpdf import FPDF


def pdf_bytes(*pages: str) -> bytes:
    pdf = FPDF()
    pdf.set_auto_page_break(auto=False)
    for text in pages:
        pdf.add_page()
        if text:
            pdf.set_font("Helvetica", size=12)
            pdf.multi_cell(0, 8, text)
    return bytes(pdf.output())
