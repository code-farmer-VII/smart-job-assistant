import os

def parse_file(file_path: str) -> str:
    """
    Parses text from various file formats (.txt, .md, .pdf, .docx).
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
        
    ext = os.path.splitext(file_path)[1].lower()
    
    if ext in ['.txt', '.md', '.json', '.csv']:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            return f.read()
            
    elif ext == '.pdf':
        try:
            from pypdf import PdfReader
            reader = PdfReader(file_path)
            text = ""
            for page in reader.pages:
                extracted = page.extract_text()
                if extracted:
                    text += extracted + "\n"
            return text
        except ImportError:
            return "Error: pypdf is not installed. Run pip install pypdf."
        except Exception as e:
            return f"Error parsing PDF: {str(e)}"
            
    elif ext == '.docx':
        try:
            import docx
            doc = docx.Document(file_path)
            return "\n".join([para.text for para in doc.paragraphs])
        except ImportError:
            return "Error: python-docx is not installed. Run pip install python-docx."
        except Exception as e:
            return f"Error parsing DOCX: {str(e)}"
            
    else:
        raise ValueError(f"Unsupported file extension: {ext}. Only .txt, .pdf, and .docx are supported for extraction.")
