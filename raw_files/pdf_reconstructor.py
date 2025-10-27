from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import Color
from PyPDF2 import PdfReader, PdfWriter
import io
import os
import json

def register_arial_font():
    """Register Arial font for English text"""
    arial_paths = [
        'fonts/arial_ms/Arial Unicode MS Bold.otf',
        'fonts/arial_ms/Arial Unicode MS.otf',
    ]
    
    # Register Regular variant
    regular_registered = False
    for font_path in arial_paths:
        if 'bd' not in font_path and 'bi' not in font_path and os.path.exists(font_path):
            try:
                pdfmetrics.registerFont(TTFont('Arial', font_path))
                print(f"Arial Regular registered from: {font_path}")
                regular_registered = True
                break
            except Exception as e:
                print(f"Error registering Arial Regular: {e}")
    
    # Register Bold variant
    bold_registered = False
    for font_path in arial_paths:
        if 'bd' in font_path and os.path.exists(font_path):
            try:
                pdfmetrics.registerFont(TTFont('Arial-Bold', font_path))
                print(f"Arial Bold registered from: {font_path}")
                bold_registered = True
                break
            except Exception as e:
                print(f"Error registering Arial Bold: {e}")
    
    # Register Italic variant
    italic_registered = False
    for font_path in arial_paths:
        if 'i' in font_path and 'bi' not in font_path and os.path.exists(font_path):
            try:
                pdfmetrics.registerFont(TTFont('Arial-Italic', font_path))
                print(f"Arial Italic registered from: {font_path}")
                italic_registered = True
                break
            except Exception as e:
                print(f"Error registering Arial Italic: {e}")
    
    # Register BoldItalic variant
    bolditalic_registered = False
    for font_path in arial_paths:
        if 'bi' in font_path and os.path.exists(font_path):
            try:
                pdfmetrics.registerFont(TTFont('Arial-BoldItalic', font_path))
                print(f"Arial BoldItalic registered from: {font_path}")
                bolditalic_registered = True
                break
            except Exception as e:
                print(f"Error registering Arial BoldItalic: {e}")
    
    if not any([regular_registered, bold_registered, italic_registered, bolditalic_registered]):
        print("Arial fonts not found. Using Helvetica fallback")
    
    return regular_registered, bold_registered, italic_registered, bolditalic_registered

def get_font_variant(is_bold, is_italic, regular_available, bold_available, italic_available, bolditalic_available):
    """Get appropriate font variant"""
    if not any([regular_available, bold_available, italic_available, bolditalic_available]):
        if is_bold and is_italic:
            return "Helvetica-BoldOblique"
        elif is_bold:
            return "Helvetica-Bold"
        elif is_italic:
            return "Helvetica-Oblique"
        else:
            return "Helvetica"
    
    if is_bold and is_italic and bolditalic_available:
        return "Arial-BoldItalic"
    elif is_bold and bold_available:
        return "Arial-Bold"
    elif is_italic and italic_available:
        return "Arial-Italic"
    elif regular_available:
        return "Arial"
    else:
        return "Helvetica"

def set_font_and_color(c, is_bold, is_italic, font_size, color, regular_available, bold_available, italic_available, bolditalic_available):
    """Set font and color with proper variant"""
    try:
        font_variant = get_font_variant(is_bold, is_italic, regular_available, bold_available, italic_available, bolditalic_available)
        c.setFont(font_variant, font_size)
    except Exception:
        if is_bold and is_italic:
            c.setFont("Helvetica-BoldOblique", font_size)
        elif is_bold:
            c.setFont("Helvetica-Bold", font_size)
        elif is_italic:
            c.setFont("Helvetica-Oblique", font_size)
        else:
            c.setFont("Helvetica", font_size)
    
    # Set text color
    try:
        if color and len(color) >= 3:
            if len(color) == 3:
                r, g, b = [max(0, min(1, v)) for v in color]
                c.setFillColorRGB(r, g, b)
            elif len(color) == 4:
                c_c, m, y, k = [max(0, min(1, v)) for v in color]
                c.setFillColorCMYK(c_c, m, y, k)
        else:
            c.setFillColorRGB(0, 0, 0)
    except Exception:
        c.setFillColorRGB(0, 0, 0)

def create_text_overlay(json_path, overlay_pdf_path, base_pdf_path):
    """Create text overlay PDF"""
    with open(json_path, 'r', encoding='utf-8') as json_file:
        pages_data = json.load(json_file)
    
    base_pdf = PdfReader(base_pdf_path)
    regular_available, bold_available, italic_available, bolditalic_available = register_arial_font()
    
    overlay_packet = io.BytesIO()
    c = canvas.Canvas(overlay_packet)
    
    for i, page_data in enumerate(pages_data):
        if i < len(base_pdf.pages):
            base_page = base_pdf.pages[i]
            page_width = float(base_page.mediabox[2])
            page_height = float(base_page.mediabox[3])
        else:
            page_width = page_data['page_width']
            page_height = page_data['page_height']
        
        c.setPageSize((page_width, page_height))
        
        current_bold = current_italic = current_size = current_color = None
        
        for char_data in page_data['characters']:
            text = char_data['text']
            if not text.strip():
                continue
                
            x = char_data['x0']
            y = page_height - char_data['bottom']
            font_size = char_data.get('size', 12)
            is_bold = char_data.get('bold', False)
            is_italic = char_data.get('italic', False)
            color = char_data.get('color', (0, 0, 0))
            
            if (is_bold != current_bold or is_italic != current_italic or 
                font_size != current_size or color != current_color):
                
                set_font_and_color(c, is_bold, is_italic, font_size, color, regular_available, bold_available, italic_available, bolditalic_available)
                current_bold, current_italic, current_size, current_color = is_bold, is_italic, font_size, color
            
            try:
                c.drawString(x, y, text)
            except:
                try:
                    safe_text = text.encode('ascii', 'ignore').decode('ascii')
                    c.drawString(x, y, safe_text)
                except:
                    c.drawString(x, y, '?')
        
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

def reconstruct_pdf(json_path, text_removed_pdf_path, output_pdf_path):
    """Main reconstruction function"""
    overlay_pdf_path = "temp_overlay.pdf"
    
    create_text_overlay(json_path, overlay_pdf_path, text_removed_pdf_path)
    merge_pdf_layers(text_removed_pdf_path, overlay_pdf_path, output_pdf_path)
    
    try:
        os.remove(overlay_pdf_path)
        print("Temporary overlay removed")
    except:
        pass
    
    print(f"PDF reconstructed: {output_pdf_path}")