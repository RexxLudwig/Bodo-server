import argparse
import sys
import os
from src.agent.extract_ import get_resume_text
from src.agent.evaluation import stream_evaluation_report

def main():
    parser = argparse.ArgumentParser(description="ATS Resume Scorer CLI")
    parser.add_argument("--pdf", required=True, help="Path to the resume PDF file")
    parser.add_argument("--jd", required=True, help="Path to the Job Description text file, or the Job Description text itself")
    args = parser.parse_args()
    
    pdf_path = args.pdf
    jd_input = args.jd
    
    if not os.path.exists(pdf_path):
        print(f"Error: PDF file '{pdf_path}' not found.")
        sys.exit(1)
        
    if os.path.exists(jd_input):
        with open(jd_input, "r", encoding="utf-8") as f:
            job_description = f.read()
    else:
        job_description = jd_input
        
    print(f"Extracting data from {pdf_path}...")
    resume_text = get_resume_text(pdf_path)
    
    print("Evaluating resume against job description...\n")
    stream_evaluation_report(resume_text, job_description)

if __name__ == "__main__":
    main()