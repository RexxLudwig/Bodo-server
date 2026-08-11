import io
import uvicorn
from pypdf import PdfReader
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from src.llm_processing.convert_to_json import convert_resume_to_json
from src.extractor.extract_ import Extractor 

app = FastAPI()
extractor = Extractor()

# Add CORS middleware to allow connections from the frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Allow all origins (update with frontend URL in production)
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)

@app.post("/resume/pdf-scan" \
"")
async def parse_resume(file: UploadFile = File(...)):
    # Read the uploaded file contents into bytes
    pdf_bytes = await file.read()
    
    # Load the PDF from bytes (prevents stream consumption issues)
    pdf_file = io.BytesIO(pdf_bytes)
    reader = PdfReader(pdf_file)
    
    # Check if there are any pages
    if not reader.pages:
        return {"error": "PDF has no pages"}
        
    import os
    import tempfile
    
    # Save to a temporary file since Extractor requires a file path
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(pdf_bytes)
        temp_pdf_path = tmp.name
        
    try:
        # Extract URLs using the extractor
        embedded_urls = extractor.extract_urls(temp_pdf_path)
        
        # Extract text from the first page using pypdf reader
        page = reader.pages[0]
        text = page.extract_text() or ""
        
        # Convert URLs to JSON (fixed the syntax error here)
        json_format = convert_resume_to_json("\n".join(embedded_urls['urls_list']))
        with open("resume.json", "w", encoding="utf-8") as output_file:
            output_file.write(json_format)

        return {
            "filename": file.filename,
            "size_bytes": len(pdf_bytes),
            "number_of_words_in_page": len(text.split()),
            "text_of_page": text,
            "embedded_urls": embedded_urls
        }
    finally:
        # Clean up the temporary file
        if os.path.exists(temp_pdf_path):
            os.remove(temp_pdf_path)

if __name__ == "__main__":
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)