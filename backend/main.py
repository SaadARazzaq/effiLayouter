import os
from text_extractor import extract_pdf_to_json
from text_remover import remove_text
from pdf_reconstructor import reconstruct_pdf
from ar_pdf_reconstructor import reconstruct_pdf_from_line_db
from countour_mapper import PDFLineExtractor

def main_workflow():
    # Configuration
    input_pdf = "input.pdf"
    text_removed_pdf = "input_text_removed.pdf"
    json_output = "extracted_data.json"
    line_db_output = "line_db.json"
    ar_line_db_output = "ar_line_db.json"
    final_output_pdf = "english_reconstructed_input.pdf"

    print("=== PDF Text Replacement Workflow ===\n")

    # Step: Give user a choice to translate to English or Arabic (1 for English, 2 for Arabic)
    language_choice = input("Choose language for reconstruction (1 for English, 2 for Arabic): ").strip()
    
    # Step 1: Remove text from original PDF
    print("1. Removing text from original PDF...")
    remove_text(input_pdf, text_removed_pdf)
    
    if language_choice == "2":  # Arabic workflow
        final_output_pdf = "arabic_reconstructed_input.pdf"
        
        # Step 2: Extract text using contour mapper (line-based extraction)
        print("\n2. Extracting line data for Arabic processing...")
        extractor = PDFLineExtractor()
        line_db = extractor.extract_lines_from_pdf(input_pdf, line_db_output)
        
        # Step 3: Translate to Arabic
        print("\n3. Translating text to Arabic...")
        ar_line_db = extractor.translate_to_arabic(line_db, ar_line_db_output)
        
        # Step 4: Reconstruct Arabic PDF
        print("\n4. Reconstructing Arabic PDF...")
        reconstruct_pdf_from_line_db(ar_line_db_output, text_removed_pdf, final_output_pdf)
        
    else:  # English workflow (default)
        # Step 2: Extract text data to JSON
        print("\n2. Extracting character data to JSON...")
        extract_pdf_to_json(input_pdf, json_output)

        # Step 3: Reconstruct English PDF
        print("\n3. Reconstructing English PDF...")
        reconstruct_pdf(json_output, text_removed_pdf, final_output_pdf)

    print(f"\n=== Workflow Complete ===")
    print(f"Input PDF: {input_pdf}")
    print(f"Text-removed PDF: {text_removed_pdf}")
    if language_choice == "2":
        print(f"Line database: {line_db_output}")
        print(f"Arabic line database: {ar_line_db_output}")
    else:
        print(f"Extracted data: {json_output}")
    print(f"Output PDF: {final_output_pdf}")

if __name__ == "__main__":
    main_workflow()