# Project Phases: ATS & GitHub Scorer

## Phase 1: Project Initialization & Core Processing
* **Project Architecture:** Set up the basic structural foundations for the application (`app/src/`).
* **LLM Integration:** Configured Language Models (Gemini & local Gemma) inside `src/config/config.py`.
* **Data Structuring:** Developed `convert_to_json.py` using Pydantic models to parse unstructured resume text into highly structured JSON formats (Education, Experience, Projects, Skills, etc.).
* **Initial Extraction Setup:** Created `extract_.py` inside the agent folder to handle reading PDFs and extracting embedded URLs using PyMuPDF and initial OCR fallbacks.
* **API Foundation:** Started an initial iteration of the application using FastAPI to serve resume parsing endpoints.

## Phase 2: CLI Transition & Code Optimization (Recent Work)
* **Architecture Shift (API to CLI):** Removed the FastAPI implementation in `server.py` and completely transitioned the application into a Command Line Interface (CLI) using `argparse`. 
* **Dynamic CLI Inputs:** Configured the CLI to accept `--pdf` (path to resume) and `--jd` (Job description file or text string) arguments for easier terminal-based usage.
* **Extraction Optimization:** Cleaned up `app/src/agent/extract_.py` by stripping out heavy, slow OCR dependencies (`pdf2image` and `pytesseract`) to prioritize fast text and hyperlink extraction using `fitz` and Regular Expressions.
* **Full-Fledged Reporting:** Implemented real-time console streaming for the evaluation report using LangChain's `.stream()`. The application now provides an immediate, streamed output detailing:
  * Overall ATS Score (out of 100)
  * Job Compatibility Score (out of 100)
  * Detailed breakdown of matching and missing skills
  * Specific suggestions for resume improvement tailored to the provided job description.

## Phase 3: Detailed Evaluation System & GitHub Integration (Current)
* **Prompt Orchestration:** Developed `PromptOrchestrator` (`orechestrator.py`) using Jinja2 templates to construct highly structured, section-by-section LLM evaluation prompts (covering Education, Internships, Projects, Skills, etc.) with specific scoring rubrics adding up to a total of 100 marks.
* **GitHub Integration without Tokens:** Implemented `GitHubParser` (`github_parser.py`) to extract a candidate's profile data without needing authentication tokens. It strategically uses the unauthenticated GitHub API to fetch top-starred repositories and merged open-source PRs, while fetching `README.md` files directly from `raw.githubusercontent.com` to bypass rate limits and conserve the 60 requests/hour IP allowance.
