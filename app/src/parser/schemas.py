from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class ContactInfo(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None

class Experience(BaseModel):
    company: Optional[str] = None
    role: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    description: List[str] = Field(default_factory=list)

class Project(BaseModel):
    name: Optional[str] = None
    description: List[str] = Field(default_factory=list)
    technologies: List[str] = Field(default_factory=list)
    link: Optional[str] = None

class Education(BaseModel):
    institution: Optional[str] = None
    degree: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None

class Certification(BaseModel):
    name: Optional[str] = None
    issuer: Optional[str] = None
    date: Optional[str] = None

class Links(BaseModel):
    github: Optional[str] = None
    linkedin: Optional[str] = None
    portfolio: Optional[str] = None
    other: List[str] = Field(default_factory=list)

class ResumeData(BaseModel):
    contact: ContactInfo = Field(default_factory=ContactInfo)
    experience: List[Experience] = Field(default_factory=list)
    projects: List[Project] = Field(default_factory=list)
    skills: List[str] = Field(default_factory=list)
    education: List[Education] = Field(default_factory=list)
    certifications: List[Certification] = Field(default_factory=list)
    links: Links = Field(default_factory=Links)
