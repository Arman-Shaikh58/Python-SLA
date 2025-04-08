import fitz  # PyMuPDF
import pytesseract
from PIL import Image
import io

# Optional: If you're on Windows, set the tesseract path
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def extract_text_from_image_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    extracted_text = ""

    for page_number in range(len(doc)):
        page = doc.load_page(page_number)
        pix = page.get_pixmap(dpi=300)  # Render page to image at 300 DPI
        img = Image.open(io.BytesIO(pix.tobytes("png")))  # Convert to PIL Image

        # OCR the image
        text = pytesseract.image_to_string(img)
        extracted_text += f"\n\n--- Page {page_number + 1} ---\n{text}"

    return extracted_text

# Example usage
pdf_file = "CO.pdf"
text_output = extract_text_from_image_pdf(pdf_file)

# Save or print the result
with open("extracted_text.txt", "w", encoding="utf-8") as f:
    f.write(text_output)

print("✅ OCR completed. Text saved to extracted_text.txt")
