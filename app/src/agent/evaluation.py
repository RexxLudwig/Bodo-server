from src.config.config import get_llm
from langchain_core.messages import HumanMessage

def stream_evaluation_report(resume_text: str, job_description: str):
    llm = get_llm()
    prompt = f"""
You are an expert ATS (Applicant Tracking System) and HR recruiter.
I will provide you with a Resume and a Job Description.
Please provide a full-fledged evaluation report.

Requirements:
1. Provide an overall ATS Score (out of 100).
2. Provide a Job Compatibility Score (out of 100).
3. Detailed breakdown of matching skills and missing skills.
4. Suggestions for improving the resume for this specific job.

Job Description:
{job_description}

Resume:
{resume_text}
"""
    print("\n" + "="*50)
    print("ATS Scoring Report")
    print("="*50 + "\n")
    try:
        for chunk in llm.stream([HumanMessage(content=prompt)]):
            print(chunk.content, end="", flush=True)
    except Exception as e:
        print(f"\nError during LLM inference: {e}")
    print("\n\n" + "="*50)
    print("End of Report")
    print("="*50 + "\n")
