import os
from pypdf import PdfReader
from docx import Document
from colorama import Fore, Style

class ResumeParser:
    """
    A dedicated class to handle file reading. 
    It supports PDF and DOCX formats.
    """
    
    @staticmethod
    def extract_text(file_path):
        """
        Determines the file type and extracts text content.
        """
        # 1. Validate file existence
        if not os.path.exists(file_path):
            print(f"{Fore.RED}Error: File not found at {file_path}{Style.RESET_ALL}")
            return None

        # 2. Check extension
        _, file_extension = os.path.splitext(file_path)
        file_extension = file_extension.lower()

        try:
            if file_extension == '.pdf':
                return ResumeParser._read_pdf(file_path)
            elif file_extension == '.docx':
                return ResumeParser._read_docx(file_path)
            else:
                print(f"{Fore.RED}Error: Unsupported file format. Use .pdf or .docx{Style.RESET_ALL}")
                return None
        except Exception as e:
            print(f"{Fore.RED}Error reading file: {e}{Style.RESET_ALL}")
            return None

    @staticmethod
    def _read_pdf(file_path):
        """Helper to read PDFs using pypdf"""
        reader = PdfReader(file_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        return text.strip()

    @staticmethod
    def _read_docx(file_path):
        """Helper to read Word docs using python-docx"""
        doc = Document(file_path)
        text = ""
        for para in doc.paragraphs:
            text += para.text + "\n"
        return text.strip()