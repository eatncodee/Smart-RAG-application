from pypdf import PdfReader
from docx import Document
import io


def extract_text_from_pdf(file_content: bytes) -> str:
    try:
        pdf_file = io.BytesIO(file_content)
        reader = PdfReader(pdf_file)
        
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        
        return text.strip()
    
    except Exception as e:
        raise ValueError(f"Error processing PDF: {str(e)}")
    

def extract_text_from_docx(file_content: bytes) -> str:
    try:
        docx_file = io.BytesIO(file_content)
        doc = Document(docx_file)
        
        text = ""
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
        
        return text.strip()
    
    except Exception as e:
        raise ValueError(f"Error processing DOCX: {str(e)}")
    

def extract_text_from_txt(file_content: bytes) -> str:
    try:
        return file_content.decode('utf-8')
    
    except Exception as e:
        raise ValueError(f"Error processing TXT: {str(e)}")


def process_file(filename: str, file_content: bytes) -> str:
    filename_lower = filename.lower()
    
    if filename_lower.endswith('.pdf'):
        return extract_text_from_pdf(file_content)
    
    elif filename_lower.endswith('.docx'):
        return extract_text_from_docx(file_content)
    
    elif filename_lower.endswith('.txt'):
        return extract_text_from_txt(file_content)
    
    else:
        raise ValueError(f"Unsupported file type. Supported: PDF, DOCX, TXT")

def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 200) -> list[str]:
    chunks = []
    start = 0
    
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]        
        if end < len(text):
            last_period = chunk.rfind('.')
            last_newline = chunk.rfind('\n')
            break_point = max(last_period, last_newline)
            
            if break_point > chunk_size // 2:
                chunk = chunk[:break_point + 1]
                end = start + break_point + 1
        
        chunks.append(chunk.strip())
        start = end - overlap  
    
    return [c for c in chunks if c]