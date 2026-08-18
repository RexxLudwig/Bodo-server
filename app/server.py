import argparse
import sys
import os
from src.agent.extract_ import get_resume_text
from src.agent.evaluation import stream_evaluation_report

def main():
    parser = argparse.ArgumentParser(description="ATS Resume Scorer CLI")
    parser.add_argument("--resume", required=True, help="Path to the resume file (.pdf or .txt)")
    parser.add_argument("--jd", required=True, help="Path to the Job Description text file, or the Job Description text itself")
    args = parser.parse_args()
    
    resume_path = args.resume
    jd_input = args.jd
    
    if not os.path.exists(resume_path):
        print(f"Error: Resume file '{resume_path}' not found.")
        sys.exit(1)
        
    if os.path.exists(jd_input):
        with open(jd_input, "r", encoding="utf-8") as f:
            job_description = f.read()
    else:
        job_description = jd_input
        
    print(f"Extracting data from {resume_path}...")
    
    if resume_path.lower().endswith(".pdf"):
        resume_text = get_resume_text(resume_path)
    elif resume_path.lower().endswith(".txt"):
        with open(resume_path, "r", encoding="utf-8") as f:
            resume_text = f.read()
    else:
        print(f"Error: Unsupported file format for '{resume_path}'. Please provide a .pdf or .txt file.")
        sys.exit(1)
    
    print("Evaluating resume against job description...\n")
    stream_evaluation_report(resume_text, job_description)

if __name__ == "__main__":
    main()