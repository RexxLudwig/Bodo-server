import json
import os
from pydantic import BaseModel, Field
from typing import List, Optional
from dotenv import load_dotenv
from config.config import get_llm

load_dotenv()

class ContactInfo(BaseModel):
    phone: Optional[str] = Field(description="Phone number")
    email: Optional[str] = Field(description="Email address")
    location: Optional[str] = Field(description="City, Country or general location")

class Links(BaseModel):
    linkedin: Optional[str] = Field(description="LinkedIn URL or identifier")
    portfolio: Optional[str] = Field(description="Portfolio URL or identifier")
    github: Optional[str] = Field(description="GitHub URL or identifier")

class Education(BaseModel):
    institution: str = Field(description="Name of the university or school")
    location: Optional[str] = Field(description="Location of the institution")
    degree: str = Field(description="Degree and field of study")
    dates: str = Field(description="Duration or graduation year")
    relevant_courses: List[str] = Field(description="List of relevant courses")

class Experience(BaseModel):
    company: str = Field(description="Name of the company")
    location: Optional[str] = Field(description="Location of the job")
    role: str = Field(description="Job title")
    dates: str = Field(description="Duration of employment")
    achievements: List[str] = Field(description="Bullet points of achievements and responsibilities")

class Project(BaseModel):
    name: str = Field(description="Name of the project")
    tech_stack: List[str] = Field(description="List of technologies used")
    description: List[str] = Field(description="Bullet points describing the project")

class Skills(BaseModel):
    languages: List[str] = Field(default_factory=list)
    ai_and_llms: List[str] = Field(default_factory=list)
    backend_and_apis: List[str] = Field(default_factory=list)
    cloud_and_devops: List[str] = Field(default_factory=list)
    developer_tools: List[str] = Field(default_factory=list)
    specializations: List[str] = Field(default_factory=list)

class Resume(BaseModel):
    name: str
    contact_info: ContactInfo
    links: Links
    education: List[Education]
    experience: List[Experience]
    projects: List[Project]
    skills: Skills
    achievements_and_certifications: List[str]

def convert_resume_to_json(text: str) -> str:
    """Converts raw resume text to a structured JSON string using the configured model."""
    llm = get_llm()
    structured_llm = llm.with_structured_output(Resume)
    
    prompt = (
        "You are an expert resume parser. Extract the information from the provided resume text into the given structured format. Do your best to extract all details correctly.\n\n"
        f"Resume Text:\n{text}"
    )
    
    parsed_resume = structured_llm.invoke(prompt)
    if isinstance(parsed_resume, BaseModel):
        return parsed_resume.model_dump_json(indent=2)
    elif isinstance(parsed_resume, dict):
        return json.dumps(parsed_resume, indent=2)
    return json.dumps(parsed_resume, indent=2)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Convert raw resume text to structured JSON.")
    parser.add_argument("--input", default="resume.txt", help="Input text file containing resume")
    parser.add_argument("--output", default="resume.json", help="Output JSON file")
    
    args = parser.parse_args()
    
    if not os.path.exists(args.input):
        print(f"Error: {args.input} not found.")
        exit(1)
        
    with open(args.input, "r") as f:
        raw_text = f.read()
        
    print(f"Parsing {args.input}...")
    json_output = convert_resume_to_json(raw_text)
    
    with open(args.output, "w") as f:
        f.write(json_output)
        
    print(f"Successfully wrote structured JSON to {args.output}")
    