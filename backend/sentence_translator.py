import json
from deep_translator import GoogleTranslator
import logging

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

def translate_sentences(sentences_json_path, output_json_path, target_lang='ar'):
    """
    Translate sentences and prepare for reconstruction
    """
    with open(sentences_json_path, 'r', encoding='utf-8') as f:
        sentences = json.load(f)
    
    translator = GoogleTranslator(source='auto', target=target_lang)
    is_rtl = target_lang in ['ar', 'he', 'fa', 'ur']
    
    translated_sentences = []
    
    for i, sentence in enumerate(sentences):
        print(f"Translating sentence {i + 1}/{len(sentences)}")
        print(f"  Original: '{sentence['text'][:80]}...'")
        
        try:
            translated_text = translator.translate(sentence['text'])
            print(f"  Translated: '{translated_text[:80]}...'")
            
            translated_sentences.append({
                "original_text": sentence['text'],
                "translated_text": translated_text,
                "page": sentence['page'],
                "is_rtl": is_rtl
            })
            
        except Exception as e:
            print(f"Error translating sentence: {e}")
            # Keep original text if translation fails
            translated_sentences.append({
                "original_text": sentence['text'],
                "translated_text": sentence['text'],  # Fallback to original
                "page": sentence['page'],
                "is_rtl": is_rtl
            })
        
        print()  # Empty line for readability
    
    with open(output_json_path, 'w', encoding='utf-8') as f:
        json.dump(translated_sentences, f, indent=4, ensure_ascii=False)
    
    print(f"Translation complete! Saved to {output_json_path}")
    return translated_sentences

def reconstruct_pdf_from_sentences(translated_sentences_json, text_removed_pdf_path, output_pdf_path):
    """
    Simple reconstruction - just overlay text on the PDF
    """
    import fitz  # PyMuPDF
    from reportlab.pdfgen import canvas
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from PyPDF2 import PdfReader, PdfWriter
    import io
    
    with open(translated_sentences_json, 'r', encoding='utf-8') as f:
        translated_sentences = json.load(f)
    
    # Group sentences by page
    sentences_by_page = {}
    for sentence in translated_sentences:
        page_num = sentence['page']
        if page_num not in sentences_by_page:
            sentences_by_page[page_num] = []
        sentences_by_page[page_num].append(sentence)
    
    # Open the text-removed PDF
    base_pdf = PdfReader(text_removed_pdf_path)
    
    # Create overlay PDF
    overlay_packet = io.BytesIO()
    c = canvas.Canvas(overlay_packet)
    
    for page_num, sentences in sentences_by_page.items():
        if page_num - 1 < len(base_pdf.pages):
            base_page = base_pdf.pages[page_num - 1]
            page_width = float(base_page.mediabox[2])
            page_height = float(base_page.mediabox[3])
        else:
            # Use default page size if page doesn't exist
            page_width = 612
            page_height = 792
        
        c.setPageSize((page_width, page_height))
        
        # Simple placement - just put sentences in order from top to bottom
        y_position = page_height - 50  # Start 50 points from top
        
        for i, sentence in enumerate(sentences):
            text = sentence['translated_text']
            
            # Set font
            try:
                c.setFont('Helvetica', 12)
            except:
                c.setFont('Helvetica', 12)
            
            c.setFillColorRGB(0, 0, 0)  # Black text
            
            # Draw the translated text
            try:
                c.drawString(50, y_position, text)
            except:
                try:
                    safe_text = text.encode('utf-8', 'ignore').decode('utf-8')
                    c.drawString(50, y_position, safe_text)
                except:
                    c.drawString(50, y_position, "Translation Error")
            
            y_position -= 20  # Move down for next sentence
        
        c.showPage()
    
    c.save()
    overlay_packet.seek(0)
    overlay_pdf = PdfReader(overlay_packet)
    
    # Merge with base PDF
    output_writer = PdfWriter()
    
    for i in range(len(base_pdf.pages)):
        base_page = base_pdf.pages[i]
        if i < len(overlay_pdf.pages):
            base_page.merge_page(overlay_pdf.pages[i])
        output_writer.add_page(base_page)
    
    with open(output_pdf_path, 'wb') as output_file:
        output_writer.write(output_file)
    
    print(f"Reconstructed PDF saved: {output_pdf_path}")