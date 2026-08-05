from .reader import read_resume, read_pdf, read_docx, read_resume_from_bytes
from .extractor import ResumeExtractor
from .schemas import ResumeData, ContactInfo, Links, Experience, Project, Education, Certification

def parse_resume(file_path: str) -> ResumeData:
    """
    Reads a resume from a file and parses it deterministically into structured data.
    """
    text = read_resume(file_path)
    extractor = ResumeExtractor(text)
    return extractor.parse()

def parse_resume_from_bytes(file_bytes: bytes, filename: str) -> ResumeData:
    """
    Reads a resume from memory (bytes) and parses it deterministically into structured data.
    """
    text = read_resume_from_bytes(file_bytes, filename)
    extractor = ResumeExtractor(text)
    return extractor.parse()
