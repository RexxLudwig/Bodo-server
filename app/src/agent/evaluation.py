import json
import concurrent.futures
from pydantic import BaseModel, Field
from typing import List

from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.status import Status
from rich import print as rprint

from src.config.config import get_llm
from langchain_core.messages import HumanMessage
from prompts.orechestrator import orchestrator
from src.llm_processing.convert_to_json import convert_resume_to_json
from src.agent.github_parser import GitHubParser

# --- Pydantic Models for Structured Output ---
class SectionEvaluation(BaseModel):
    score: float = Field(description="The final score for this section")
    feedback: str = Field(description="Detailed evaluation feedback and scoring breakdown")

class GitHubEvaluation(SectionEvaluation):
    vulnerabilities: str = Field(description="Vulnerabilities and red flags, or 'None detected'")

class OverallEvaluation(SectionEvaluation):
    recommendation: str = Field(description="Final hire/no-hire recommendation with justifications")

class JobCompatibilityEvaluation(BaseModel):
    job_compatibility_score: int
    matching_skills: List[str]
    missing_skills: List[str]
    improvement_suggestions: str

# --- Helper function for evaluation ---
def evaluate_section(prompt: str, pydantic_model: BaseModel):
    llm = get_llm()
    structured_llm = llm.with_structured_output(pydantic_model)
    return structured_llm.invoke([HumanMessage(content=prompt)])

def extract_github_username(links: dict) -> str:
    github_url = links.get("github", "")
    if not github_url:
        return ""
    parts = github_url.rstrip('/').split('/')
    if parts:
        return parts[-1]
    return ""

def stream_evaluation_report(resume_text: str, job_description: str):
    console = Console()
    
    console.print(Panel.fit("[bold cyan]✨ Starting Comprehensive ATS Evaluation ✨[/bold cyan]", border_style="cyan"))
    
    with Status("[bold green]Parsing resume into structured JSON...", spinner="dots") as status:
        resume_json_str = convert_resume_to_json(resume_text)
        try:
            resume_data = json.loads(resume_json_str)
        except Exception:
            resume_data = {"links": {}}
            
        status.update("[bold green]Fetching GitHub data...")
        github_username = extract_github_username(resume_data.get("links", {}))
        github_data = ""
        if github_username:
            try:
                parser = GitHubParser()
                github_data = parser.extract_all(github_username)
                console.print(f"  [dim]✓ Successfully fetched GitHub data for {github_username}[/dim]")
            except Exception as e:
                console.print(f"  [red]✗ Failed to fetch GitHub data: {e}[/red]")
                github_data = "Error fetching GitHub data."
        else:
            console.print("  [dim]✗ No GitHub URL found in resume.[/dim]")

        status.update("[bold green]Running AI evaluations simultaneously (this may take a minute)...")
        
        # Render all prompts
        prompts = {
            "basics": orchestrator.render_basics(resume_text),
            "education": orchestrator.render_education(resume_json_str, job_description),
            "skills": orchestrator.render_skills(resume_text, job_description),
            "projects": orchestrator.render_projects(resume_text),
            "internships": orchestrator.render_internships(resume_text),
            "github": orchestrator.render_github(github_data),
            "awards": orchestrator.render_awards_achievements(resume_text),
        }
        
        results = {}
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = {
                "basics": executor.submit(evaluate_section, prompts["basics"], SectionEvaluation),
                "education": executor.submit(evaluate_section, prompts["education"], SectionEvaluation),
                "skills": executor.submit(evaluate_section, prompts["skills"], SectionEvaluation),
                "projects": executor.submit(evaluate_section, prompts["projects"], SectionEvaluation),
                "internships": executor.submit(evaluate_section, prompts["internships"], SectionEvaluation),
                "github": executor.submit(evaluate_section, prompts["github"], GitHubEvaluation),
                "awards": executor.submit(evaluate_section, prompts["awards"], SectionEvaluation),
            }
            for name, future in futures.items():
                try:
                    results[name] = future.result()
                except Exception as e:
                    if name == "github":
                        results[name] = GitHubEvaluation(score=0, feedback="Evaluation failed.", vulnerabilities="Unknown")
                    else:
                        results[name] = SectionEvaluation(score=0, feedback="Evaluation failed.")

        status.update("[bold green]Finalizing evaluation and computing job compatibility...")
        
        # Max scores per section to prevent LLM hallucinations (e.g. returning percentages instead of raw marks)
        max_scores = {
            "basics": 2,
            "education": 15,
            "skills": 6,
            "projects": 15,
            "internships": 25,
            "github": 20,
            "awards": 10
        }
        
        total_score = 0
        candidate_summary = ""
        
        for name, res in results.items():
            if hasattr(res, 'score'):
                # Hard clamp the score to prevent the total from exceeding 100
                max_allowed = max_scores.get(name, 0)
                if res.score > max_allowed:
                    # If it's suspiciously large (like a percentage), scale it down
                    if res.score <= 100 and max_allowed > 0:
                        res.score = round((res.score / 100.0) * max_allowed, 1)
                    else:
                        res.score = max_allowed
                
                total_score += res.score
                candidate_summary += f"{name.capitalize()} Score: {res.score}/{max_allowed}\nFeedback: {res.feedback}\n\n"
        
        candidate_summary = f"Total preliminary score: {total_score}/93\n\n" + candidate_summary
            
        eval_criteria_prompt = orchestrator.render_evaluation_criteria(candidate_summary, job_description)
        presentation_res = evaluate_section(eval_criteria_prompt, OverallEvaluation)
        
        # Clamp presentation score
        if presentation_res.score > 7:
            presentation_res.score = 7
            
        total_score += presentation_res.score
        total_score = round(total_score, 1)

        job_compat_prompt = orchestrator.render_job_compatibility(resume_json_str, job_description)
        job_compat_res = evaluate_section(job_compat_prompt, JobCompatibilityEvaluation)

    # Compile Final Report
    final_report = orchestrator.render_template(
        'final_report',
        total_score=total_score,
        job_compatibility=f"{job_compat_res.job_compatibility_score}/100",
        internships_score=results["internships"].score,
        internships_feedback=results["internships"].feedback,
        github_score=results["github"].score,
        github_feedback=results["github"].feedback,
        projects_score=results["projects"].score,
        projects_feedback=results["projects"].feedback,
        education_score=results["education"].score,
        education_feedback=results["education"].feedback,
        awards_score=results["awards"].score,
        awards_feedback=results["awards"].feedback,
        presentation_score=presentation_res.score,
        presentation_feedback=presentation_res.feedback,
        skills_score=results["skills"].score,
        skills_feedback=results["skills"].feedback,
        basics_score=results["basics"].score,
        basics_feedback=results["basics"].feedback,
        vulnerabilities=results["github"].vulnerabilities,
        recommendation=presentation_res.recommendation
    )

    console.print("\n")
    console.rule("[bold cyan]FINAL ATS REPORT[/bold cyan]")
    
    # Print the markdown report beautifully
    console.print(Markdown(final_report))
    
    # Print Job Compatibility in a nice Panel
    compat_text = (
        f"[bold bright_green]Matching Skills:[/bold bright_green] {', '.join(job_compat_res.matching_skills)}\n\n"
        f"[bold bright_red]Missing Skills:[/bold bright_red] {', '.join(job_compat_res.missing_skills)}\n\n"
        f"[bold bright_yellow]Improvement Suggestions:[/bold bright_yellow]\n{job_compat_res.improvement_suggestions}"
    )
    console.print(Panel(compat_text, title="🎯 Job Compatibility Specifics", border_style="magenta"))
    console.print("\n")
