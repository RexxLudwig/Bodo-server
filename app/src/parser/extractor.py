import re
from typing import Dict, Any, List
from .schemas import ResumeData, ContactInfo, Links, Experience, Project, Education, Certification

class ResumeExtractor:
    def __init__(self, text: str):
        self.text = text
        self.lines = text.split('\n')
        self.sections = self._segment_sections()
        
    def _segment_sections(self) -> Dict[str, str]:
        """A heuristic approach to find sections like EXPERIENCE, EDUCATION, SKILLS, etc."""
        sections = {}
        current_section = "header"
        sections[current_section] = []
        
        # Common section headers
        headers = [
            "experience", "work experience", "employment history", "employment", "professional experience",
            "education", "academic background",
            "skills", "technical skills", "core competencies",
            "projects", "personal projects",
            "certifications", "licenses",
            "summary", "profile", "objective"
        ]
        
        for line in self.lines:
            line_cleaned = line.strip().lower()
            if line_cleaned in headers or (len(line_cleaned) < 30 and line_cleaned.strip(':') in headers):
                current_section = line_cleaned.strip(':')
                sections[current_section] = []
            else:
                if line.strip():
                    sections[current_section].append(line)
                    
        return {k: "\n".join(v) for k, v in sections.items()}

    def extract_contact(self) -> ContactInfo:
        header_text = self.sections.get("header", self.text[:1500])
        
        # Email extraction
        email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        emails = re.findall(email_pattern, header_text)
        email = emails[0] if emails else None
        
        # Phone extraction
        phone_pattern = r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
        phones = re.findall(phone_pattern, header_text)
        phone = phones[0] if phones else None
        
        # Name extraction (heuristic: first non-empty line in header that isn't contact info)
        name = None
        for line in header_text.split('\n'):
            line = line.strip()
            if line and not re.search(email_pattern, line) and not re.search(phone_pattern, line):
                # Usually name is 1-4 words and doesn't contain a lot of numbers or symbols
                if len(line.split()) <= 4 and not re.search(r'\d', line):
                    name = line
                    break
                    
        return ContactInfo(name=name, email=email, phone=phone)

    def extract_links(self) -> Links:
        links = Links()
        
        # Full URLs
        url_pattern = r'https?://(?:www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b(?:[-a-zA-Z0-9()@:%_\+.~#?&//=]*)'
        urls = re.findall(url_pattern, self.text)
        
        # Loose URLs (e.g. github.com/user)
        loose_url_pattern = r'(?:github\.com|linkedin\.com/in|[\w-]+\.github\.io)[/\w-]*'
        loose_urls = re.findall(loose_url_pattern, self.text)
        
        all_urls = set(urls + loose_urls)
        
        for url in all_urls:
            url_lower = url.lower()
            if 'github.com' in url_lower:
                links.github = url
            elif 'linkedin.com' in url_lower:
                links.linkedin = url
            elif 'portfolio' in url_lower or '.io' in url_lower or '.dev' in url_lower:
                links.portfolio = url
            else:
                if url not in links.other:
                    links.other.append(url)
                    
        return links
        
    def extract_skills(self) -> List[str]:
        skills = []
        for key, text in self.sections.items():
            if 'skill' in key:
                # Split by commas or bullet points
                tokens = re.split(r'[,|•\n]', text)
                skills.extend([s.strip() for s in tokens if s.strip() and len(s.strip()) > 1])
                
        # Deduplicate while preserving order
        return list(dict.fromkeys(skills))

    def extract_experience(self) -> List[Experience]:
        # Phase 1: Basic extraction. Deterministic parsing of experience blocks is highly 
        # dependent on resume format. We can implement a simplified rule set here.
        experiences = []
        return experiences

    def extract_projects(self) -> List[Project]:
        projects = []
        return projects

    def extract_education(self) -> List[Education]:
        education = []
        return education

    def extract_certifications(self) -> List[Certification]:
        certs = []
        return certs

    def parse(self) -> ResumeData:
        return ResumeData(
            contact=self.extract_contact(),
            links=self.extract_links(),
            skills=self.extract_skills(),
            experience=self.extract_experience(),
            projects=self.extract_projects(),
            education=self.extract_education(),
            certifications=self.extract_certifications()
        )
