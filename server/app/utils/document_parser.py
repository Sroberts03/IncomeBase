import fitz  # PyMuPDF
import base64
import logging

logger = logging.getLogger(__name__)

class DocumentParser:
    @staticmethod
    def parse(file_bytes: bytes, file_name: str) -> dict | None:
        """Determines if a file is digital text or needs Vision OCR."""
        
        # 1. MAGIC NUMBER DETECTION (Trust the bytes, not the name)
        ext = ""
        if file_bytes.startswith(b'%PDF'):
            ext = ".pdf"
        elif file_bytes.startswith(b'\xff\xd8\xff'):
            ext = ".jpg"
        elif file_bytes.startswith(b'\x89PNG\r\n\x1a\n'):
            ext = ".png"
        else:
            # Fallback to checking the filename if magic numbers fail
            ext = "." + file_name.split(".")[-1].lower() if "." in file_name else ""
            if ext not in [".pdf", ".jpg", ".jpeg", ".png"]:
                return None
        
        try:
            # 2. PARSE BASED ON DETECTED TYPE
            if ext == ".pdf":
                doc = fitz.open(stream=file_bytes, filetype="pdf")
                full_text = "".join([page.get_text() for page in doc])
                
                if len(full_text.strip()) > 50:
                    return {"type": "text", "content": full_text, "name": file_name}
                
                page = doc.load_page(0)
                pix = page.get_pixmap()
                img_data = base64.b64encode(pix.tobytes()).decode("utf-8")
                return {"type": "image", "content": img_data, "name": file_name}

            elif ext in [".jpg", ".jpeg", ".png"]:
                img_data = base64.b64encode(file_bytes).decode("utf-8")
                return {"type": "image", "content": img_data, "name": file_name}
            
            elif ext in [".txt", ".csv"]:
                text_content = file_bytes.decode("utf-8", errors="ignore")
                return {"type": "text", "content": text_content, "name": file_name}
            
            else:
                logger.warning(f"Unsupported or unrecognized file type for file: {file_name}")
                return None

        except Exception as e:
            logger.error(f"Parser failed reading {file_name}: {str(e)}")
            return None