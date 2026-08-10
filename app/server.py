import io
import uvicorn
from pypdf import PdfReader
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from convert_to_json import convert_resume_to_json

app = FastAPI()

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
        
    # Get the first page (index 0)
    page = reader.pages[0]
    text = page.extract_text() or ""
    json_format = convert_resume_to_json(text)
    with open("resume.josn", "w", encoding="utf-8") as output_file:
        output_file.write(json_format)

    
    return {
        "filename": file.filename,
        "size_bytes": len(pdf_bytes),
        "number_of_words_in_page": len(text.split()),
        "text_of_page": text
    } 

if __name__ == "__main__":
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)