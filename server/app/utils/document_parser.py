import fitz  # PyMuPDF
import base64
from pathlib import Path

class DocumentParser:
    @staticmethod
    def parse(file_path: Path) -> dict:
        """Determines if a file is digital text or needs Vision OCR."""
        ext = file_path.suffix.lower()
        
        if ext == ".pdf":
            doc = fitz.open(file_path)
            # Extract text from all pages
            full_text = "".join([page.get_text() for page in doc])
            
            # If the PDF has actual text, use it (Fast Track)
            if len(full_text.strip()) > 50:
                return {"type": "text", "content": full_text, "name": file_path.name}
            
            # If it's a scanned PDF, convert the first page to base64 (Vision Track)
            page = doc.load_page(0)
            pix = page.get_pixmap()
            img_data = base64.b64encode(pix.tobytes()).decode("utf-8")
            return {"type": "image", "content": img_data, "name": file_path.name}

        elif ext in [".jpg", ".jpeg", ".png"]:
            with open(file_path, "rb") as f:
                img_data = base64.b64encode(f.read()).decode("utf-8")
            return {"type": "image", "content": img_data, "name": file_path.name}
            
        return None