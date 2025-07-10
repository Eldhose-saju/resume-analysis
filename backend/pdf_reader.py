import io
from PyPDF2 import PdfReader
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def extract_text_from_pdf(file):
    """
    Extract text from uploaded PDF file with better error handling
    """
    try:
        # Reset file pointer to beginning
        file.seek(0)
        
        # Read file content into memory
        file_content = file.read()
        
        # Check if file is empty
        if not file_content:
            raise ValueError("Uploaded file is empty")
        
        # Create BytesIO object from file content
        pdf_stream = io.BytesIO(file_content)
        
        # Read PDF
        pdf_reader = PdfReader(pdf_stream)
        
        # Check if PDF has pages
        if len(pdf_reader.pages) == 0:
            raise ValueError("PDF file has no pages")
        
        # Extract text from all pages
        text = ""
        for page_num, page in enumerate(pdf_reader.pages):
            try:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
                logger.info(f"Successfully extracted text from page {page_num + 1}")
            except Exception as e:
                logger.warning(f"Failed to extract text from page {page_num + 1}: {str(e)}")
                continue
        
        # Check if any text was extracted
        if not text.strip():
            raise ValueError("No text could be extracted from the PDF. The PDF might be image-based or corrupted.")
        
        logger.info(f"Successfully extracted {len(text)} characters from PDF")
        return text.strip()
        
    except Exception as e:
        logger.error(f"Error extracting text from PDF: {str(e)}")
        raise Exception(f"PDF processing failed: {str(e)}")

def validate_pdf_file(file):
    """
    Validate if the uploaded file is a valid PDF
    """
    try:
        # Reset file pointer
        file.seek(0)
        
        # Read first few bytes to check PDF signature
        header = file.read(4)
        file.seek(0)  # Reset again
        
        if header != b'%PDF':
            raise ValueError("File is not a valid PDF")
        
        return True
        
    except Exception as e:
        raise ValueError(f"Invalid PDF file: {str(e)}")

# Alternative function using pdfplumber (if you want to try a different library)
def extract_text_with_pdfplumber(file):
    """
    Alternative PDF text extraction using pdfplumber
    Note: You'll need to install pdfplumber first: pip install pdfplumber
    """
    try:
        import pdfplumber
        
        file.seek(0)
        file_content = file.read()
        pdf_stream = io.BytesIO(file_content)
        
        text = ""
        with pdfplumber.open(pdf_stream) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        
        if not text.strip():
            raise ValueError("No text could be extracted from the PDF")
        
        return text.strip()
        
    except ImportError:
        raise ImportError("pdfplumber is not installed. Install it with: pip install pdfplumber")
    except Exception as e:
        raise Exception(f"PDF processing failed: {str(e)}")