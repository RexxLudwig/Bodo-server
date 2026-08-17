## An AI-powered ATS (Applicant Tracking System) scorer that evaluates candidates based on their GitHub projects and contributions.

## Features

- 📄 Multi-format resume parsing (PDF, DOCX, TXT)
- 🔍 GitHub link extraction and validation
- 📊 Multi-factor project assessment
- 🤖 AI-powered code quality analysis
- 💯 Weighted scoring system
- 📈 Beautiful console output

## Installation

```bash
# Clone the repository
git clone <repository-url>
cd ats-github-scorer

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Copy and configure environment variables
cp .env.example .env
# Edit .env with your API keys


#Run this to get the ats score
python server.py --pdf my_resume.pdf --jd my_job_description.txt