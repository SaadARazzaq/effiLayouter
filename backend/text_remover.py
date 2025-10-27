import fitz  # PyMuPDF
import logging
import sys

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

def remove_text_from_pdf(input_pdf, output_pdf):
    """Remove all text from PDF while preserving images and structure"""
    logging.info(f"Opening PDF: {input_pdf}")
    doc = fitz.open(input_pdf)

    for page_num in range(len(doc)):
        page = doc[page_num]
        logging.info(f"Processing page {page_num + 1}...")

        blocks = page.get_text("rawdict")  # extract structured content
        for b in blocks["blocks"]:
            if b["type"] == 0:  # text block
                logging.debug(f"Removing text block: {b}")
                page.add_redact_annot(b["bbox"])
        page.apply_redactions(images=fitz.PDF_REDACT_IMAGE_NONE)  # keep images intact

    logging.info(f"Writing cleaned PDF to: {output_pdf}")
    doc.save(output_pdf, deflate=True, garbage=4)
    logging.info("Text removal completed successfully ✅")

def remove_text(input_pdf, output_pdf):
    """Public function for text removal"""
    remove_text_from_pdf(input_pdf, output_pdf)