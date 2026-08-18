import os
from pathlib import Path
from jinja2 import Environment, FileSystemLoader, TemplateNotFound

# Determine the absolute path to the templates directory
# Note: folder is named "tempaltes" as per the existing directory structure
PROMPTS_DIR = Path(__file__).parent
TEMPLATES_DIR = PROMPTS_DIR / "tempaltes"

class PromptOrchestrator:
    def __init__(self, templates_dir: str | Path = TEMPLATES_DIR):
        """Initialize the Jinja environment with the given templates directory."""
        self.env = Environment(
            loader=FileSystemLoader(str(templates_dir)),
            autoescape=False,  # We are rendering text prompts for LLMs, not HTML
            trim_blocks=True,
            lstrip_blocks=True
        )

    def render_template(self, template_name: str, **kwargs) -> str:
        """
        Renders a given Jinja template with the provided keyword arguments.
        
        Args:
            template_name (str): The name of the template file (e.g., 'basics.jinja2').
            **kwargs: Variables to pass to the Jinja template (e.g., resume_text).
            
        Returns:
            str: The rendered prompt.
        """
        if not template_name.endswith('.jinja2'):
            template_name += '.jinja2'
            
        try:
            template = self.env.get_template(template_name)
            return template.render(**kwargs)
        except TemplateNotFound:
            raise FileNotFoundError(f"Template '{template_name}' not found in {self.env.loader.searchpath}.")

    def render_basics(self, resume_text: str) -> str:
        return self.render_template('basics', resume_text=resume_text)
        
    def render_education(self, resume_text: str, job_description: str = None) -> str:
        return self.render_template('education', resume_text=resume_text, job_description=job_description)
        
    def render_skills(self, resume_text: str, job_description: str = None) -> str:
        return self.render_template('skills', resume_text=resume_text, job_description=job_description)
        
    def render_projects(self, resume_text: str) -> str:
        return self.render_template('projects', resume_text=resume_text)
        
    def render_internships(self, resume_text: str) -> str:
        return self.render_template('internships', resume_text=resume_text)
        
    def render_github(self, github_data: str) -> str:
        return self.render_template('github', github_data=github_data)
        
    def render_awards_achievements(self, resume_text: str) -> str:
        return self.render_template('awards_achievements', resume_text=resume_text)
        
    def render_evaluation_criteria(self, candidate_data: str, job_description: str = None) -> str:
        return self.render_template('resume_evaluation_criteria', candidate_data=candidate_data, job_description=job_description)

    def render_job_compatibility(self, resume_json_format: str, job_description: str) -> str:
        return self.render_template('job_compatibility', resume_json_format=resume_json_format, job_description=job_description)

# Provide a default singleton instance for easy imports across the app
orchestrator = PromptOrchestrator()
