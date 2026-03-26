import fitz  # PyMuPDF
import base64
from pathlib import Path

class DocumentParser:
    @staticmethod
    def parse(file_bytes: bytes, file_name: str) -> dict:
        """Determines if a file is digital text or needs Vision OCR."""
        ext = "." + file_name.split(".")[-1].lower() if "." in file_name else ""
        
        if ext == ".pdf":
            # fitz.open can take stream and filetype
            doc = fitz.open(stream=file_bytes, filetype="pdf")
            # Extract text from all pages
            full_text = "".join([page.get_text() for page in doc])
            
            # If the PDF has actual text, use it (Fast Track)
            if len(full_text.strip()) > 50:
                return {"type": "text", "content": full_text, "name": file_name}
            
            # If it's a scanned PDF, convert the first page to base64 (Vision Track)
            page = doc.load_page(0)
            pix = page.get_pixmap()
            img_data = base64.b64encode(pix.tobytes()).decode("utf-8")
            return {"type": "image", "content": img_data, "name": file_name}

        elif ext in [".jpg", ".jpeg", ".png"]:
            img_data = base64.b64encode(file_bytes).decode("utf-8")
            return {"type": "image", "content": img_data, "name": file_name}
            
        return None