import fitz 

def mirror_pdf_horizontally(input_pdf, output_pdf):
    """Mirror/Flip PDF horizontally for RTL language support"""
    print(f"Mirroring PDF horizontally: {input_pdf}")
    
    # Open the input PDF
    doc = fitz.open(input_pdf)
    
    # Create a new PDF for output
    output_doc = fitz.open()
    
    for page_num in range(len(doc)):
        page = doc[page_num]
        print(f"Mirroring page {page_num + 1}...")
        
        # Get page dimensions
        page_width = page.rect.width
        page_height = page.rect.height
        
        # Create a new page with same dimensions
        new_page = output_doc.new_page(width=page_width, height=page_height)
        
        # Create transformation matrix for horizontal mirroring
        # This flips the page horizontally: scale(-1, 1) and translate(page_width, 0)
        matrix = fitz.Matrix(-1, 0, 0, 1, page_width, 0)
        
        # Get the pixmap of the original page
        pix = page.get_pixmap(matrix=matrix)
        
        # Insert the mirrored pixmap as an image
        img_data = pix.tobytes("png")
        img_rect = fitz.Rect(0, 0, page_width, page_height)
        new_page.insert_image(img_rect, stream=img_data)
    
    # Save the mirrored PDF
    output_doc.save(output_pdf)
    output_doc.close()
    doc.close()
    
    print(f"Mirrored PDF saved: {output_pdf}")
    return output_pdf