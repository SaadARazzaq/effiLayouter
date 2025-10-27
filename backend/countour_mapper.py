import pdfplumber
import json
import os
import re
import fitz  # PyMuPDF
import uuid
from datetime import datetime
from collections import defaultdict
import logging
import time
import sys
import random
import argostranslate.package
import argostranslate.translate
import wordninja
from concurrent.futures import ThreadPoolExecutor, as_completed

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class PDFLineExtractor:
    """Optimized PDF line extraction with bounding boxes"""
    
    def __init__(self):
        self.line_cache = {}
        self.translation_installed = False
        self._install_translation_package()
    
    def _install_translation_package(self):
        """Install Argos Translate English to Arabic package"""
        try:
            logger.info("Checking for Argos Translate English to Arabic package...")
            
            # Update package index
            argostranslate.package.update_package_index()
            
            # Get available packages
            available_packages = argostranslate.package.get_available_packages()
            
            # Find English to Arabic package
            package_to_install = next(
                filter(
                    lambda x: x.from_code == "en" and x.to_code == "ar", 
                    available_packages
                ),
                None
            )
            
            if package_to_install:
                logger.info(f"Installing English to Arabic translation package...")
                argostranslate.package.install_from_path(package_to_install.download())
                self.translation_installed = True
                logger.info("Translation package installed successfully!")
            else:
                logger.warning("English to Arabic package not found. Translation will be disabled.")
                self.translation_installed = False
                
        except Exception as e:
            logger.error(f"Failed to install translation package: {e}")
            self.translation_installed = False
    
    def _preprocess_for_translation(self, text):
        """Preprocess text for better translation: lowercase and split concatenated words"""
        if not text or not text.strip():
            return text
        
        # Convert to lowercase
        processed_text = text.lower()
        
        # Use wordninja to split concatenated words
        try:
            # Split into words using wordninja
            split_words = wordninja.split(processed_text)
            # Rejoin with spaces
            processed_text = " ".join(split_words)
        except Exception as e:
            logger.warning(f"Wordninja processing failed for text: {text[:50]}... Error: {e}")
            # If wordninja fails, keep the lowercase text
        
        return processed_text
    
    def extract_lines_from_pdf(self, pdf_path, json_path=None):
        """Extract lines with bounding boxes from PDF with optimized processing"""
        if json_path is None:
            base_name = os.path.splitext(pdf_path)[0]
            json_path = f"{base_name}_line_db.json"
        
        logger.info(f"Starting extraction from: {pdf_path}")
        
        lines_data = []
        total_lines = 0
        total_characters = 0
        total_words = 0
        
        try:
            with pdfplumber.open(pdf_path) as pdf:
                total_pages = len(pdf.pages)
                
                for page_num, page in enumerate(pdf.pages, 1):
                    logger.info(f"Processing page {page_num}")
                    
                    # Extract words with minimal attributes for efficiency
                    words = page.extract_words(extra_attrs=["size", "fontname", "x0", "top", "x1", "bottom"])
                    if not words:
                        continue
                    
                    # Group words into lines using efficient approach
                    page_lines = self._group_words_into_lines(words, page_num)
                    total_lines += len(page_lines)
                    
                    for line in page_lines:
                        total_characters += len(line["text"])
                        total_words += line["word_count"]
                    
                    lines_data.extend(page_lines)
                    
                    # Clear memory after processing each page
                    del words
            
            # Create simplified database structure
            line_db = {
                "metadata": {
                    "pdf_file": os.path.basename(pdf_path),
                    "file_size": os.path.getsize(pdf_path) if os.path.exists(pdf_path) else 0,
                    "extraction_date": datetime.now().isoformat(),
                    "total_pages": total_pages,
                    "total_sentences": total_lines,
                    "total_characters": total_characters,
                    "total_words": total_words
                },
                "sentences": lines_data
            }
            
            # Save with optimized JSON formatting
            self._save_optimized_json(line_db, json_path)
            
            logger.info(f"Extraction complete. Total lines: {total_lines}")
            return line_db
            
        except Exception as e:
            logger.error(f"Error processing PDF: {e}")
            raise

    def translate_to_arabic(self, line_db, output_json_path=None, max_workers=2, timeout_seconds=120):
        """Translate English text to Arabic with rate limiting and human-like behavior"""
        if not self.translation_installed:
            logger.error("Translation package not installed. Cannot translate to Arabic.")
            return line_db
        
        if output_json_path is None:
            base_name = line_db["metadata"]["pdf_file"].replace(".pdf", "")
            output_json_path = f"{base_name}_ar_line_db.json"
        
        logger.info(f"Starting Arabic translation...")
        
        # Create a copy of the line database for Arabic
        ar_line_db = {
            "metadata": line_db["metadata"].copy(),
            "sentences": []
        }
        
        # Add translation metadata
        ar_line_db["metadata"]["translation"] = {
            "target_language": "ar",
            "translation_date": datetime.now().isoformat(),
            "translation_service": "ArgosTranslate",
            "preprocessing": "lowercase + wordninja"
        }
        
        # Prepare sentences for translation
        sentences_to_translate = []
        for sentence in line_db["sentences"]:
            if sentence["text"].strip():  # Only translate non-empty text
                sentences_to_translate.append(sentence)
        
        # Translate in batches to avoid timeout issues
        batch_size = 20
        translated_count = 0
        total_to_translate = len(sentences_to_translate)
        
        for i in range(0, len(sentences_to_translate), batch_size):
            batch = sentences_to_translate[i:i + batch_size]
            logger.info(f"Processing batch {i//batch_size + 1}/{(len(sentences_to_translate)-1)//batch_size + 1}")
            
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                # Submit translation tasks for this batch
                future_to_sentence = {
                    executor.submit(self._translate_sentence_with_delay, sentence): sentence 
                    for sentence in batch
                }
                
                # Process completed translations with longer timeout per batch
                try:
                    for future in as_completed(future_to_sentence, timeout=timeout_seconds):
                        original_sentence = future_to_sentence[future]
                        try:
                            translated_text = future.result()
                            if translated_text:
                                # Create Arabic sentence with same structure
                                ar_sentence = original_sentence.copy()
                                ar_sentence["text"] = translated_text
                                ar_sentence["language"] = "ar"
                                # Store original text for reference
                                ar_sentence["original_text"] = original_sentence["text"]
                                ar_line_db["sentences"].append(ar_sentence)
                                
                                translated_count += 1
                                if translated_count % 10 == 0:
                                    logger.info(f"Translated {translated_count}/{total_to_translate} sentences")
                            
                        except Exception as e:
                            logger.warning(f"Failed to translate sentence: {e}")
                            # Keep original text if translation fails
                            ar_sentence = original_sentence.copy()
                            ar_sentence["translation_error"] = str(e)
                            ar_line_db["sentences"].append(ar_sentence)
                            
                except TimeoutError:
                    logger.warning(f"Batch {i//batch_size + 1} timed out. Continuing with next batch.")
                    # Add untranslated sentences from this batch
                    for sentence in batch:
                        ar_sentence = sentence.copy()
                        ar_sentence["translation_error"] = "timeout"
                        ar_line_db["sentences"].append(ar_sentence)
            
            # Small delay between batches to avoid overwhelming the system
            time.sleep(1)
        
        # Save Arabic line database
        self._save_optimized_json(ar_line_db, output_json_path)
        logger.info(f"Arabic translation complete. Translated {translated_count}/{total_to_translate} sentences")
        
        return ar_line_db

    def _translate_sentence_with_delay(self, sentence):
        """Translate a single sentence with human-like delays and error handling"""
        original_text = sentence["text"].strip()
        if not original_text:
            return ""
        
        # Skip very short or non-translatable text
        if len(original_text) < 2 or original_text.isdigit() or all(not c.isalnum() for c in original_text):
            return original_text
        
        # Preprocess text for better translation
        processed_text = self._preprocess_for_translation(original_text)
        
        # Human-like delay (0.1-0.5 seconds - much faster since it's local)
        delay = random.uniform(0.1, 0.5)
        time.sleep(delay)
        
        try:
            # No character limit needed for Argos Translate (handles long text well)
            # Translate the text with retry logic
            max_retries = 2
            for attempt in range(max_retries):
                try:
                    translated = argostranslate.translate.translate(processed_text, "en", "ar")
                    
                    # Additional short delay after successful translation
                    time.sleep(random.uniform(0.1, 0.3))
                    
                    return translated
                    
                except Exception as e:
                    if attempt < max_retries - 1:
                        # Wait longer before retrying
                        retry_delay = random.uniform(1.0, 2.0)
                        logger.warning(f"Translation attempt {attempt + 1} failed, retrying in {retry_delay:.1f}s: {e}")
                        time.sleep(retry_delay)
                    else:
                        raise
            
        except Exception as e:
            logger.error(f"Translation error for '{original_text[:50]}...': {e}")
            # Return empty string to indicate failure
            return ""
    
    def _group_words_into_lines(self, words, page_num):
        """Efficiently group words into lines using vertical clustering"""
        if not words:
            return []
        
        # Sort words by vertical position for efficient line grouping
        words_sorted = sorted(words, key=lambda w: w['top'])
        
        # Use clustering to group words into lines
        lines = []
        current_line = []
        line_y_center = None
        
        for word in words_sorted:
            word_y_center = (word['top'] + word['bottom']) / 2
            
            if not current_line:
                # Start first line
                current_line.append(word)
                line_y_center = word_y_center
                continue
            
            # Check if word belongs to current line (within tolerance)
            y_tolerance = word.get('size', 12) * 0.4  # Dynamic tolerance based on font size
            
            if abs(word_y_center - line_y_center) <= y_tolerance:
                current_line.append(word)
                # Update line center as weighted average
                line_y_center = (line_y_center * (len(current_line) - 1) + word_y_center) / len(current_line)
            else:
                # Finalize current line and start new one
                if current_line:
                    line_obj = self._create_line_object(current_line, page_num)
                    lines.append(line_obj)
                
                current_line = [word]
                line_y_center = word_y_center
        
        # Add the last line
        if current_line:
            line_obj = self._create_line_object(current_line, page_num)
            lines.append(line_obj)
        
        return lines
    
    def _create_line_object(self, words, page_num):
        """Create a line object from words with optimized data structure"""
        # Sort words horizontally
        words_sorted = sorted(words, key=lambda w: w['x0'])
        
        # Calculate bounding box efficiently
        x0 = min(word['x0'] for word in words_sorted)
        y0 = min(word['top'] for word in words_sorted)
        x1 = max(word['x1'] for word in words_sorted)
        y1 = max(word['bottom'] for word in words_sorted)
        
        # Extract text and normalize it (remove spaces between characters)
        raw_text = ' '.join(word['text'] for word in words_sorted)
        normalized_text = self._normalize_text(raw_text)
        
        # Get font information
        font_sizes = [word.get('size', 0) for word in words_sorted]
        font_names = [word.get('fontname', '') for word in words_sorted if word.get('fontname')]
        
        # Determine if text is bold or italic
        is_bold = any('bold' in name.lower() for name in font_names)
        is_italic = any('italic' in name.lower() for name in font_names)
        
        # Get primary font and size
        primary_font = font_names[0] if font_names else ""
        primary_size = font_sizes[0] if font_sizes else 0
        
        # Create compact line object
        return {
            "id": str(uuid.uuid4())[:8],  # Short unique ID
            "text": normalized_text,
            "bbox": [round(x0, 2), round(y0, 2), round(x1, 2), round(y1, 2)],
            "page": page_num,
            "word_count": len(normalized_text.split()),
            "font": primary_font,
            "size": round(primary_size, 2),
            "bold": is_bold,
            "italic": is_italic,
            "coordinates": {
                "top_left": {"x": round(x0, 2), "y": round(y0, 2)},
                "bottom_right": {"x": round(x1, 2), "y": round(y1, 2)}
            }
        }
    
    def _normalize_text(self, text):
        """Advanced text normalization to fix spacing issues in PDF text extraction"""
        if not text or len(text.strip()) == 0:
            return text
            
        # Store original for comparison
        original = text
        
        # First, try to detect if this is a case where each character is separated by spaces
        if self._is_character_by_character_text(text):
            # Use advanced algorithm to reconstruct words from spaced characters
            text = self._reconstruct_text_from_spaced_characters(text)
        
        # Fix specific patterns that commonly appear in PDFs
        text = self._fix_common_patterns(text)
        
        # Final cleanup of any remaining odd spacing patterns
        text = self._final_text_cleanup(text)
        
        # If normalization made it worse or empty, return original
        if not text or len(text) < len(original) / 2:
            return original
            
        return text
    
    def _is_character_by_character_text(self, text):
        """Check if text appears to have spaces between each character"""
        if not text:
            return False
            
        # Split into parts
        parts = text.split()
        
        # If most parts are single characters, it's likely character-by-character text
        if len(parts) < 3:
            return False
            
        single_char_count = sum(1 for part in parts if len(part) == 1 and part.isalpha())
        total_alpha_parts = sum(1 for part in parts if part.isalpha())
        
        # If we have at least 3 alpha parts and most are single characters
        if total_alpha_parts >= 3 and single_char_count >= total_alpha_parts * 0.7:
            return True
            
        return False
    
    def _reconstruct_text_from_spaced_characters(self, text):
        """Reconstruct proper text from spaced-out characters"""
        parts = text.split()
        reconstructed = []
        current_word = []
        
        for i, part in enumerate(parts):
            # Check if this part looks like it should be part of a word
            is_char = len(part) == 1 and part.isalpha()
            has_next_char = (i < len(parts) - 1 and 
                           len(parts[i + 1]) == 1 and 
                           parts[i + 1].isalpha())
            
            # If this is a character and next is too, add to current word
            if is_char and has_next_char:
                current_word.append(part)
            # If this is a character but next isn't, finish the word
            elif is_char and not has_next_char:
                current_word.append(part)
                reconstructed.append(''.join(current_word))
                current_word = []
            # If this isn't a character but we have a current word, finish it
            elif not is_char and current_word:
                reconstructed.append(''.join(current_word))
                reconstructed.append(part)
                current_word = []
            # Otherwise just add the part as is
            else:
                reconstructed.append(part)
        
        # Add any remaining word being built
        if current_word:
            reconstructed.append(''.join(current_word))
        
        return ' '.join(reconstructed)
    
    def _fix_common_patterns(self, text):
        """Fix common patterns that appear in PDF text extraction"""
        # Fix numbers with spaces (e.g., "20 21" -> "2021")
        text = re.sub(r'(\d)\s+(\d)', r'\1\2', text)
        
        # Fix URLs and email addresses
        text = re.sub(r'(\w)\s+([@./])\s*', r'\1\2', text)  # Remove spaces around @ . /
        text = re.sub(r'\s+([@./])\s+', r'\1', text)  # Remove spaces around special chars
        
        # Fix hyphenated words and compound terms
        text = re.sub(r'(\w)\s*-\s*(\w)', r'\1-\2', text)  # Remove spaces around hyphens
        
        # Fix parentheses and brackets
        text = re.sub(r'\(\s+', '(', text)  # Remove space after (
        text = re.sub(r'\s+\)', ')', text)  # Remove space before )
        
        # Fix commas and other punctuation
        text = re.sub(r',\s+', ', ', text)  # Ensure single space after comma
        text = re.sub(r'\s+,', ',', text)  # Remove space before comma
        
        return text
    
    def _final_text_cleanup(self, text):
        """Final cleanup of text after reconstruction"""
        # Fix punctuation spacing
        text = re.sub(r'\s+([.,;:!?])', r'\1', text)  # Remove space before punctuation
        text = re.sub(r'([.,;:!?])(?=\w)', r'\1 ', text)  # Add space after punctuation if followed by word
        
        # Clean up multiple spaces
        text = re.sub(r'\s+', ' ', text)
        
        return text.strip()
    
    def _save_optimized_json(self, data, file_path):
        """Save JSON with optimized formatting"""
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            # Use separators to minimize file size but keep it readable
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def visualize_lines(self, pdf_path, line_db, output_path=None):
        """Create PDF with bounding boxes around lines (optimized)"""
        if output_path is None:
            base_name = os.path.splitext(pdf_path)[0]
            output_path = f"{base_name}_visualized.pdf"
        
        logger.info(f"Creating visualization: {output_path}")
        
        try:
            pdf_document = fitz.open(pdf_path)
            
            # Group lines by page for efficient processing
            lines_by_page = defaultdict(list)
            for line in line_db["sentences"]:
                lines_by_page[line["page"]].append(line)
            
            # Process each page
            for page_num, page_lines in lines_by_page.items():
                if page_num > len(pdf_document):
                    continue
                
                page = pdf_document[page_num - 1]
                
                # Draw all bounding boxes for this page
                for line in page_lines:
                    x0, y0, x1, y1 = line["bbox"]
                    rect = fitz.Rect(x0, y0, x1, y1)
                    page.draw_rect(rect, color=(0, 1, 0), fill=None, width=1.0, overlay=True)
            
            # Save with optimized compression
            pdf_document.save(output_path, garbage=4, deflate=True)
            pdf_document.close()
            
            logger.info(f"Visualization saved: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Error creating visualization: {e}")
            raise

# Example usage with performance monitoring
if __name__ == "__main__":
    # Start timer
    start_time = time.time()
    
    # Initialize extractor
    extractor = PDFLineExtractor()
    
    try:
        # Process PDF
        pdf_path = "input.pdf"  # Replace with your PDF path
        
        # Extract lines
        line_db = extractor.extract_lines_from_pdf(pdf_path)
        
        # Create visualization
        visualized_pdf_path = extractor.visualize_lines(pdf_path, line_db)
        
        # Translate to Arabic with more conservative settings
        ar_line_db = extractor.translate_to_arabic(line_db, max_workers=1, timeout_seconds=180)
        
        # Calculate and print performance metrics
        end_time = time.time()
        processing_time = end_time - start_time
        
        logger.info(f"Processing completed in {processing_time:.2f} seconds")
        logger.info(f"Total sentences extracted: {line_db['metadata']['total_sentences']}")
        logger.info(f"Visualized PDF created: {visualized_pdf_path}")
        logger.info(f"Arabic translation saved: {pdf_path.replace('.pdf', '_ar_line_db.json')}")
        
        # Print sample of results
        print("\nSample English sentences (first 5):")
        for i, line in enumerate(line_db['sentences'][:5]):
            print(f"{i+1}. [{line['id']}] {line['text'][:70]}{'...' if len(line['text']) > 70 else ''}")
        
        print("\nSample Arabic sentences (first 5):")
        for i, line in enumerate(ar_line_db['sentences'][:5]):
            print(f"{i+1}. [{line['id']}] {line['text'][:70]}{'...' if len(line['text']) > 70 else ''}")
            
        # Print summary statistics
        metadata = line_db["metadata"]
        print(f"\nSummary Statistics:")
        print(f"Total characters: {metadata['total_characters']}")
        print(f"Total words: {metadata['total_words']}")
        print(f"Total sentences: {metadata['total_sentences']}")
        
    except Exception as e:
        logger.error(f"Failed to process PDF: {e}")
        import traceback
        traceback.print_exc()