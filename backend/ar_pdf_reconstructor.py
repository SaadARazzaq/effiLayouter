from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import Color
from reportlab.lib.utils import simpleSplit
from PyPDF2 import PdfReader, PdfWriter
import io
import os
import json
import re
import arabic_reshaper
from bidi.algorithm import get_display

def register_arabic_fonts():
    """Register Arabic fonts for text rendering"""
    arabic_font_paths = [
        'fonts/noto/NotoNaskhArabic-Bold.ttf',
        'fonts/noto/NotoNaskhArabic-Regular.ttf',
    ]
    
    # Register Regular variant
    regular_registered = False
    for font_path in arabic_font_paths:
        if 'Bold' not in font_path and os.path.exists(font_path):
            try:
                pdfmetrics.registerFont(TTFont('Arabic-Regular', font_path))
                print(f"Arabic Regular registered from: {font_path}")
                regular_registered = True
                break
            except Exception as e:
                print(f"Error registering Arabic Regular: {e}")
    
    # Register Bold variant
    bold_registered = False
    for font_path in arabic_font_paths:
        if 'Bold' in font_path and os.path.exists(font_path):
            try:
                pdfmetrics.registerFont(TTFont('Arabic-Bold', font_path))
                print(f"Arabic Bold registered from: {font_path}")
                bold_registered = True
                break
            except Exception as e:
                print(f"Error registering Arabic Bold: {e}")
    
    return regular_registered, bold_registered

def get_arabic_font_variant(is_bold, regular_available, bold_available):
    """Get appropriate Arabic font variant"""
    if is_bold and bold_available:
        return "Arabic-Bold"
    elif regular_available:
        return "Arabic-Regular"
    else:
        # Fallback to any available font
        try:
            if bold_available:
                return "Arabic-Bold"
            elif regular_available:
                return "Arabic-Regular"
            else:
                return "Helvetica"
        except:
            return "Helvetica"

def set_arabic_font_and_color(c, is_bold, font_size, regular_available, bold_available):
    """Set Arabic font and color with proper variant"""
    try:
        font_variant = get_arabic_font_variant(is_bold, regular_available, bold_available)
        c.setFont(font_variant, font_size)
    except Exception as e:
        print(f"Error setting Arabic font: {e}")
        c.setFont("Helvetica", font_size)
    
    # Set text color to black
    c.setFillColorRGB(0, 0, 0)

def process_arabic_text(text):
    """Process Arabic text for proper RTL rendering"""
    if not text or not any('\u0600' <= c <= '\u06FF' for c in text):
        return text  # Return as-is if not Arabic text
    
    try:
        # Reshape Arabic text
        reshaped_text = arabic_reshaper.reshape(text)
        # Apply bidirectional algorithm for RTL
        processed_text = get_display(reshaped_text)
        return processed_text
    except Exception as e:
        print(f"Error processing Arabic text: {e}")
        return text

def create_text_overlay_from_line_db(json_path, overlay_pdf_path, base_pdf_path):
    """Create text overlay PDF from line database JSON"""
    with open(json_path, 'r', encoding='utf-8') as json_file:
        line_db = json.load(json_file)
    
    base_pdf = PdfReader(base_pdf_path)
    regular_available, bold_available = register_arabic_fonts()
    
    overlay_packet = io.BytesIO()
    c = canvas.Canvas(overlay_packet)
    
    # Group sentences by page
    sentences_by_page = {}
    for sentence in line_db['sentences']:
        page_num = sentence['page'] - 1  # Convert to 0-based index
        if page_num not in sentences_by_page:
            sentences_by_page[page_num] = []
        sentences_by_page[page_num].append(sentence)
    
    # Process each page
    for page_num in range(len(base_pdf.pages)):
        if page_num not in sentences_by_page:
            # Create empty page if no sentences
            base_page = base_pdf.pages[page_num]
            page_width = float(base_page.mediabox[2])
            page_height = float(base_page.mediabox[3])
            c.setPageSize((page_width, page_height))
            c.showPage()
            continue
            
        base_page = base_pdf.pages[page_num]
        page_width = float(base_page.mediabox[2])
        page_height = float(base_page.mediabox[3])
        
        c.setPageSize((page_width, page_height))
        
        current_bold = current_size = None
        
        for sentence in sentences_by_page[page_num]:
            text = sentence['text']
            if not text.strip():
                continue
                
            # Process Arabic text for RTL rendering
            processed_text = process_arabic_text(text)
            
            # Get coordinates (using top_left as reference point)
            x = sentence['coordinates']['top_left']['x']
            y = page_height - sentence['coordinates']['top_left']['y'] - sentence.get('size', 12) * 0.8  # Adjust for baseline
            
            font_size = sentence.get('size', 12)
            is_bold = sentence.get('bold', False)
            
            # Set font and color if changed
            if (is_bold != current_bold or font_size != current_size):
                set_arabic_font_and_color(c, is_bold, font_size, regular_available, bold_available)
                current_bold, current_size = is_bold, font_size
            
            try:
                # Draw the text at the calculated position
                c.drawString(x, y, processed_text)
            except Exception as e:
                print(f"Error drawing text '{text}': {e}")
                try:
                    # Try with simple text
                    c.drawString(x, y, text[:50])  # Truncate if too long
                except:
                    # Fallback to simple text
                    c.drawString(x, y, '...')
        
        c.showPage()
    
    c.save()
    overlay_packet.seek(0)
    overlay_pdf = PdfReader(overlay_packet)
    
    with open(overlay_pdf_path, 'wb') as overlay_file:
        overlay_writer = PdfWriter()
        for page in overlay_pdf.pages:
            overlay_writer.add_page(page)
        overlay_writer.write(overlay_file)
    
    print(f"Text overlay created: {overlay_pdf_path}")

def merge_pdf_layers(base_pdf_path, overlay_pdf_path, output_pdf_path):
    """Merge base PDF with text overlay"""
    base_pdf = PdfReader(base_pdf_path)
    overlay_pdf = PdfReader(overlay_pdf_path)
    
    output_writer = PdfWriter()
    
    for i in range(len(base_pdf.pages)):
        base_page = base_pdf.pages[i]
        if i < len(overlay_pdf.pages):
            base_page.merge_page(overlay_pdf.pages[i])
        output_writer.add_page(base_page)
    
    with open(output_pdf_path, 'wb') as output_file:
        output_writer.write(output_file)
    
    print(f"Merged PDF saved: {output_pdf_path}")

def reconstruct_pdf_from_line_db(json_path, base_pdf_path, output_pdf_path):
    """Main reconstruction function for line database JSON"""
    overlay_pdf_path = "temp_line_overlay.pdf"
    
    create_text_overlay_from_line_db(json_path, overlay_pdf_path, base_pdf_path)
    merge_pdf_layers(base_pdf_path, overlay_pdf_path, output_pdf_path)
    
    try:
        os.remove(overlay_pdf_path)
        print("Temporary overlay removed")
    except:
        pass
    
    print(f"PDF reconstructed from line database: {output_pdf_path}")

# Install required packages for Arabic text processing:
# pip install arabic-reshaper python-bidi

# Example usage
if __name__ == "__main__":
    # Replace these paths with your actual file paths
    json_path = "input_ar_line_db.json"  # Your Arabic line database JSON file
    base_pdf_path = "input_no_text.pdf"  # The original PDF (for page dimensions)
    output_pdf_path = "reconstructed_document_ar.pdf"  # Output PDF
    
    reconstruct_pdf_from_line_db(json_path, base_pdf_path, output_pdf_path)