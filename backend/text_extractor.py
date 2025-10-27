import pdfplumber
import json
import os
import re

def extract_pdf_to_json(pdf_path, json_path):
    """Extract PDF text with coordinates and font information to JSON"""
    pages_data = []
    
    with pdfplumber.open(pdf_path) as pdf:
        for page_num, page in enumerate(pdf.pages):
            print(f"Extracting page {page_num + 1}...")
            
            # Extract individual characters
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