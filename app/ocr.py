import pytesseract
import os
from PIL import Image
import easyocr
from pdf2image import convert_from_path
import numpy as np
import os

# Lazy load EasyOCR reader to avoid slow startup
_reader = None

def get_easyocr_reader():
    global _reader
    if _reader is None:
        _reader = easyocr.Reader(['en'])
    return _reader

# If Tesseract is installed in a common location but not on PATH, try to set it explicitly
tesseract_common_paths = [
    r"C:\Program Files\Tesseract-OCR\tesseract.exe",
    r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
]
for _p in tesseract_common_paths:
    try:
        if os.path.exists(_p):
            pytesseract.pytesseract.tesseract_cmd = _p
            break
    except Exception:
        pass

def run_ocr(path):
    """Extract text from image or PDF using Tesseract OCR with EasyOCR fallback."""
    
    # Handle PDF files
    if path.lower().endswith('.pdf'):
        try:
            # Try converting PDF to images (default, relies on poppler in PATH)
            images = convert_from_path(path, dpi=300, first_page=1, last_page=3)  # Limit to first 3 pages
        except Exception as e:
            # If that fails, try using a common Poppler install location explicitly
            try:
                poppler_default = r"C:\Program Files\poppler\Library\bin"
                poppler_env = os.environ.get('POPPLER_PATH')
                poppler_path = poppler_env or poppler_default
                if os.path.exists(os.path.join(poppler_path, 'pdfinfo.exe')):
                    images = convert_from_path(path, dpi=300, first_page=1, last_page=3, poppler_path=poppler_path)
                else:
                    raise
            except Exception:
                print(f"PDF processing error: {e}")
                return f"Error processing PDF: {str(e)}"

        all_text = []
        for i, image in enumerate(images):
            try:
                # Try Tesseract first
                text = pytesseract.image_to_string(image)
                if text.strip():
                    all_text.append(text)
            except Exception as e:
                print(f"Tesseract failed on page {i+1}, trying EasyOCR: {e}")
                # Fallback to EasyOCR
                try:
                    reader = get_easyocr_reader()
                    # Convert PIL image to numpy array for EasyOCR
                    img_np = np.array(image)
                    text = "\n".join(reader.readtext(img_np, detail=0))
                    all_text.append(text)
                except Exception as e2:
                    print(f"EasyOCR also failed on page {i+1}: {e2}")

        return "\n\n".join(all_text) if all_text else "Could not extract text from PDF"
    
    # Handle image files
    try:
        text = pytesseract.image_to_string(Image.open(path))
        if text.strip():
            return text
    except Exception as e:
        print(f"Tesseract failed, trying EasyOCR: {e}")
    
    # Fallback to EasyOCR for images
    try:
        reader = get_easyocr_reader()
        return "\n".join(reader.readtext(path, detail=0))
    except Exception as e:
        return f"Error extracting text: {str(e)}"
