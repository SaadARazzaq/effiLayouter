# import pdfplumber
# import json

# filePath = "binance.pdf"  # Path of the file

# pages_data = []  # List to store page data with character coordinates

# """
# Extract text with precise character coordinates using pdfplumber.
# """
# with pdfplumber.open(filePath) as pdf:
#     for page_num, page in enumerate(pdf.pages):
#         print(f"Processing page {page_num + 1}...")
        
#         # Extract characters with precise coordinates
#         characters = []
#         words = page.extract_words(extra_attrs=["fontname", "size"])
        
#         # For even more granular character-level extraction:
#         page_chars = page.chars
#         for char in page_chars:
#             characters.append({
#                 "text": char["text"],
#                 "x0": char["x0"],
#                 "y0": char["y0"],
#                 "x1": char["x1"],
#                 "y1": char["y1"],
#                 "fontname": char.get("fontname", "unknown"),
#                 "size": char.get("size", 12),
#                 "top": char["top"],
#                 "bottom": char["bottom"]
#             })
        
#         # Store page data
#         pages_data.append({
#             "page_number": page_num + 1,
#             "page_width": page.width,
#             "page_height": page.height,
#             "character_count": len(characters),
#             "characters": characters,
#             "words": words  # Optional: also store word-level data
#         })

# print(f"Extracted {sum([page['character_count'] for page in pages_data])} characters from {len(pages_data)} pages")

# # Write to JSON file
# with open("output_coordinates_precise.json", "w", encoding='utf-8') as json_file:
#     json.dump(pages_data, json_file, indent=4, ensure_ascii=False)

# print("Precise coordinate data saved to output_coordinates_precise.json")

# # Print sample
# sample_data = []
# if pages_data and pages_data[0]['characters']:
#     sample_data = pages_data[0]['characters'][:10]  # First 10 characters

# print("Sample character data:")
# print(json.dumps(sample_data, indent=4, ensure_ascii=False))


# import pdfplumber
# import json
# from reportlab.pdfgen import canvas
# import os

# def extract_pdf_to_json(pdf_path, json_path):
#     """Extract PDF text with coordinates to JSON"""
#     pages_data = []
    
#     with pdfplumber.open(pdf_path) as pdf:
#         for page_num, page in enumerate(pdf.pages):
#             print(f"Extracting page {page_num + 1}...")
            
#             characters = []
#             page_chars = page.chars
            
#             for char in page_chars:
#                 characters.append({
#                     "text": char["text"],
#                     "x0": char["x0"],
#                     "y0": char["y0"],
#                     "x1": char["x1"],
#                     "y1": char["y1"],
#                     "top": char["top"],
#                     "bottom": char["bottom"],
#                     "fontname": char.get("fontname", "Helvetica"),
#                     "size": char.get("size", 12)
#                 })
            
#             pages_data.append({
#                 "page_number": page_num + 1,
#                 "page_width": page.width,
#                 "page_height": page.height,
#                 "characters": characters
#             })
    
#     with open(json_path, "w", encoding='utf-8') as json_file:
#         json.dump(pages_data, json_file, indent=4, ensure_ascii=False)
    
#     print(f"Extraction complete. Saved to {json_path}")
#     return pages_data

# def reconstruct_pdf_from_json(json_path, output_pdf_path):
#     """Reconstruct PDF from JSON data"""
#     with open(json_path, 'r', encoding='utf-8') as json_file:
#         pages_data = json.load(json_file)
    
#     c = canvas.Canvas(output_pdf_path)
    
#     for page_data in pages_data:
#         page_width = page_data['page_width']
#         page_height = page_data['page_height']
#         c.setPageSize((page_width, page_height))
        
#         for char_data in page_data['characters']:
#             text = char_data['text']
#             x = char_data['x0']
#             y = page_height - char_data['bottom']  # Convert coordinate system
            
#             font_name = char_data.get('fontname', 'Helvetica')
#             font_size = char_data.get('size', 12)
            
#             # Simple font mapping
#             font_map = {
#                 'helvetica': 'Helvetica',
#                 'times': 'Times-Roman',
#                 'courier': 'Courier',
#                 'arial': 'Helvetica'
#             }
            
#             # Use mapped font or default to Helvetica
#             base_font = 'Helvetica'
#             for key, value in font_map.items():
#                 if key in font_name.lower():
#                     base_font = value
#                     break
            
#             c.setFont(base_font, font_size)
#             c.drawString(x, y, text)
        
#         c.showPage()
    
#     c.save()
#     print(f"PDF reconstructed: {output_pdf_path}")

# # Run the complete workflow
# if __name__ == "__main__":
#     input_pdf = "binance.pdf"
#     json_output = "extracted_data.json"
#     reconstructed_pdf = "reconstructed_binance.pdf"
    
#     # Step 1: Extract PDF to JSON
#     print("Step 1: Extracting PDF to JSON...")
#     extract_pdf_to_json(input_pdf, json_output)
    
#     # Step 2: Reconstruct PDF from JSON
#     print("Step 2: Reconstructing PDF from JSON...")
#     reconstruct_pdf_from_json(json_output, reconstructed_pdf)
    
#     print("Complete workflow finished!")

import pdfplumber
import json
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import Color
import os
import re
from collections import defaultdict
from PyPDF2 import PdfReader, PdfWriter
import io

def register_arial_unicode_font():
    """Register Arial Unicode MS font for multilingual support including Arabic"""
    # Define possible paths for Arial Unicode MS .otf files
    arial_unicode_paths = [
        'fonts/arial_ms/Arial Unicode MS.otf',  # Regular font
        'fonts/arial_ms/Arial Unicode MS Bold.otf',  # Bold font
        'fonts/arial_unicode_ms/Arial Unicode MS.otf',
        'fonts/arial_unicode_ms/Arial Unicode MS Bold.otf',
        'arial_ms/Arial Unicode MS.otf',
        'arial_ms/Arial Unicode MS Bold.otf',
        'Arial Unicode MS.otf',
        'Arial Unicode MS Bold.otf'
    ]
    
    regular_registered = False
    bold_registered = False
    
    # Register Regular variant
    regular_path = None
    for font_path in arial_unicode_paths:
        if 'Bold' not in font_path and os.path.exists(font_path):
            try:
                pdfmetrics.registerFont(TTFont('ArialUnicodeMS', font_path))
                print(f"Arial Unicode MS Regular registered from: {font_path}")
                regular_registered = True
                regular_path = font_path
                break
            except Exception as e:
                print(f"Error registering Arial Unicode MS Regular from {font_path}: {e}")
    
    # Register Bold variant
    bold_path = None
    for font_path in arial_unicode_paths:
        if 'Bold' in font_path and os.path.exists(font_path):
            try:
                pdfmetrics.registerFont(TTFont('ArialUnicodeMS-Bold', font_path))
                print(f"Arial Unicode MS Bold registered from: {font_path}")
                bold_registered = True
            except Exception as e:
                print(f"Error registering Arial Unicode MS Bold from {font_path}: {e}")
    
    # Register Italic and BoldItalic using available fonts
    if regular_registered:
        try:
            # Use Regular for Italic (since we don't have separate Italic .otf)
            pdfmetrics.registerFont(TTFont('ArialUnicodeMS-Italic', regular_path))
            print("Arial Unicode MS Italic registered (using Regular font)")
        except:
            pass
    
    if bold_registered and bold_path:
        try:
            # Use Bold for BoldItalic
            pdfmetrics.registerFont(TTFont('ArialUnicodeMS-BoldItalic', bold_path))
            print("Arial Unicode MS BoldItalic registered (using Bold font)")
        except:
            pass
    
    if not regular_registered and not bold_registered:
        print("Arial Unicode MS fonts not found. Using Helvetica as fallback")
    
    return regular_registered, bold_registered

def extract_pdf_to_json(pdf_path, json_path):
    """Extract PDF text with coordinates and font information to JSON"""
    pages_data = []
    
    with pdfplumber.open(pdf_path) as pdf:
        for page_num, page in enumerate(pdf.pages):
            print(f"Extracting page {page_num + 1}...")
            
            characters = []
            page_chars = page.chars
            
            for char in page_chars:
                # Get font information
                fontname = char.get("fontname", "")
                size = char.get("size", 12)
                
                # Detect bold/italic from original font properties
                is_bold = False
                is_italic = False
                if fontname:
                    font_lower = fontname.lower()
                    is_bold = any(keyword in font_lower for keyword in 
                                 ['bold', 'bd', 'black', 'heavy', 'b', '-b', 'w6', 'w7', 'w8', 'w9'])
                    is_italic = any(keyword in font_lower for keyword in 
                                   ['italic', 'oblique', 'it', 'slanted', 'i', '-i'])
                
                # Get color information with error handling
                color = (0, 0, 0)  # Default black
                try:
                    color = char.get("non_stroking_color") or char.get("color", (0, 0, 0))
                    if color and not all(isinstance(c, (int, float)) for c in color):
                        color = (0, 0, 0)
                except:
                    color = (0, 0, 0)
                
                characters.append({
                    "text": char["text"],
                    "x0": char["x0"],
                    "y0": char["y0"],
                    "x1": char["x1"],
                    "y1": char["y1"],
                    "top": char["top"],
                    "bottom": char["bottom"],
                    "original_font": fontname,
                    "size": size,
                    "bold": is_bold,
                    "italic": is_italic,
                    "color": color
                })
            
            pages_data.append({
                "page_number": page_num + 1,
                "page_width": page.width,
                "page_height": page.height,
                "characters": characters
            })
    
    with open(json_path, "w", encoding='utf-8') as json_file:
        json.dump(pages_data, json_file, indent=4, ensure_ascii=False)
    
    print(f"Extraction complete. Saved to {json_path}")
    return pages_data

def get_arial_unicode_font_variant(is_bold, is_italic, regular_available, bold_available):
    """Get the appropriate Arial Unicode MS font variant based on available fonts"""
    if not regular_available and not bold_available:
        # Fallback to Helvetica
        if is_bold and is_italic:
            return "Helvetica-BoldOblique"
        elif is_bold:
            return "Helvetica-Bold"
        elif is_italic:
            return "Helvetica-Oblique"
        else:
            return "Helvetica"
    
    # Use available Arial Unicode MS fonts
    if is_bold and bold_available:
        if is_italic:
            return "ArialUnicodeMS-BoldItalic"
        else:
            return "ArialUnicodeMS-Bold"
    elif is_italic and regular_available:
        return "ArialUnicodeMS-Italic"
    elif regular_available:
        return "ArialUnicodeMS"
    else:
        # Fallback if only bold is available but we need regular
        return "ArialUnicodeMS-Bold"

def set_arial_unicode_font_and_color(c, is_bold, is_italic, font_size, color, regular_available, bold_available):
    """Set Arial Unicode MS font and color"""
    try:
        font_variant = get_arial_unicode_font_variant(is_bold, is_italic, regular_available, bold_available)
        c.setFont(font_variant, font_size)
    except Exception as e:
        print(f"Font error: {e}, falling back to Helvetica")
        # Fallback to standard fonts
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
        if color and len(color) >= 3 and all(isinstance(c, (int, float)) for c in color):
            if len(color) == 3:  # RGB
                r, g, b = [max(0, min(1, c)) for c in color]
                c.setFillColorRGB(r, g, b)
            elif len(color) == 4:  # CMYK
                c, m, y, k = [max(0, min(1, c)) for c in color]
                c.setFillColorCMYK(c, m, y, k)
        else:
            c.setFillColorRGB(0, 0, 0)  # Default black
    except:
        c.setFillColorRGB(0, 0, 0)

def create_text_overlay_pdf(json_path, overlay_pdf_path, base_pdf_path):
    """Create a PDF with only text overlay that matches the base PDF dimensions"""
    with open(json_path, 'r', encoding='utf-8') as json_file:
        pages_data = json.load(json_file)
    
    # Get base PDF dimensions
    base_pdf = PdfReader(base_pdf_path)
    
    # Register Arial Unicode MS fonts
    regular_available, bold_available = register_arial_unicode_font()
    
    # Create overlay PDF
    overlay_packet = io.BytesIO()
    c = canvas.Canvas(overlay_packet)
    
    for i, page_data in enumerate(pages_data):
        if i < len(base_pdf.pages):
            base_page = base_pdf.pages[i]
            # Use base PDF page size
            page_width = float(base_page.mediabox[2])
            page_height = float(base_page.mediabox[3])
        else:
            # Fallback to extracted dimensions if base PDF has fewer pages
            page_width = page_data['page_width']
            page_height = page_data['page_height']
        
        c.setPageSize((page_width, page_height))
        
        current_bold = None
        current_italic = None
        current_size = None
        current_color = None
        
        for char_data in page_data['characters']:
            text = char_data['text']
            if not text.strip():  # Skip empty text
                continue
                
            x = char_data['x0']
            y = page_height - char_data['bottom']  # Convert coordinate system
            
            font_size = char_data.get('size', 12)
            is_bold = char_data.get('bold', False)
            is_italic = char_data.get('italic', False)
            color = char_data.get('color', (0, 0, 0))
            
            # Only change font if properties have changed
            if (is_bold != current_bold or is_italic != current_italic or 
                font_size != current_size or color != current_color):
                
                set_arial_unicode_font_and_color(c, is_bold, is_italic, font_size, color, regular_available, bold_available)
                current_bold = is_bold
                current_italic = is_italic
                current_size = font_size
                current_color = color
            
            # Draw the character
            try:
                c.drawString(x, y, text)
            except Exception as e:
                # Handle problematic characters
                try:
                    safe_text = text.encode('utf-8', 'ignore').decode('utf-8')
                    c.drawString(x, y, safe_text)
                except:
                    c.drawString(x, y, '?')
        
        c.showPage()
    
    c.save()
    
    # Save overlay PDF
    overlay_packet.seek(0)
    overlay_pdf = PdfReader(overlay_packet)
    
    # Write to file
    with open(overlay_pdf_path, 'wb') as overlay_file:
        overlay_writer = PdfWriter()
        for page in overlay_pdf.pages:
            overlay_writer.add_page(page)
        overlay_writer.write(overlay_file)
    
    print(f"Text overlay PDF created: {overlay_pdf_path}")

def merge_pdf_layers(base_pdf_path, overlay_pdf_path, output_pdf_path):
    """Merge the base PDF with text overlay"""
    print("Merging base PDF with text overlay...")
    
    base_pdf = PdfReader(base_pdf_path)
    overlay_pdf = PdfReader(overlay_pdf_path)
    
    output_writer = PdfWriter()
    
    for i in range(len(base_pdf.pages)):
        base_page = base_pdf.pages[i]
        
        if i < len(overlay_pdf.pages):
            overlay_page = overlay_pdf.pages[i]
            # Merge overlay onto base page
            base_page.merge_page(overlay_page)
        
        output_writer.add_page(base_page)
    
    # Save the merged PDF
    with open(output_pdf_path, 'wb') as output_file:
        output_writer.write(output_file)
    
    print(f"Merged PDF saved: {output_pdf_path}")

def reconstruct_pdf_with_arabic_support(json_path, base_pdf_path, output_pdf_path):
    """Reconstruct PDF by overlaying text onto existing base PDF"""
    # Create temporary overlay PDF
    overlay_pdf_path = "temp_overlay.pdf"
    
    # Step 1: Create text overlay PDF
    create_text_overlay_pdf(json_path, overlay_pdf_path, base_pdf_path)
    
    # Step 2: Merge overlay with base PDF
    merge_pdf_layers(base_pdf_path, overlay_pdf_path, output_pdf_path)
    
    # Clean up temporary file
    try:
        os.remove(overlay_pdf_path)
        print("Temporary overlay file removed")
    except:
        pass
    
    print(f"PDF reconstructed with Arabic support: {output_pdf_path}")

# Run the complete workflow
if __name__ == "__main__":
    input_pdf = "binance.pdf"  # Original PDF to extract from
    base_pdf = "binance_RE.pdf"  # Existing PDF to overlay onto
    json_output = "extracted_data.json"
    reconstructed_pdf = "reconstructed_binance.pdf"
    
    # Step 1: Extract PDF to JSON
    print("Step 1: Extracting PDF to JSON...")
    extracted_data = extract_pdf_to_json(input_pdf, json_output)
    
    # Step 2: Reconstruct PDF by overlaying text onto existing PDF
    print("Step 2: Reconstructing PDF with text overlay...")
    reconstruct_pdf_with_arabic_support(json_output, base_pdf, reconstructed_pdf)
    
    print("\nComplete workflow finished!")
    print(f"Original PDF: {input_pdf}")
    print(f"Base PDF: {base_pdf}")
    print(f"JSON data: {json_output}")
    print(f"Reconstructed PDF: {reconstructed_pdf}")