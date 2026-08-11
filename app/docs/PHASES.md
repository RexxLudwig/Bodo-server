# PHASES.md

# AI ATS Scorer — Development Roadmap

## Vision

Build a production-grade AI-powered ATS scoring platform using **Graph Engineering**, **LangGraph**, **LLM Tool Calling**, and **deterministic analysis**. The system should produce transparent, explainable, and reproducible evaluations rather than relying solely on keyword matching.

---

# Phase 1 — Resume Parsing & Data Extraction

### Status
- **Completed** (Refactored with LLM configuration and JSON conversion)

### Objective

Convert resumes into structured data for downstream analysis.

### Deliverables

- [x] PDF/DOCX parsing
- [x] Section detection
- [x] Contact information extraction
- [x] Experience extraction
- [x] Project extraction
- [x] Skills extraction
- [x] Education extraction
- [x] Certification extraction
- [x] Link extraction (GitHub, LinkedIn, Portfolio)

### Output

```json
{
  "contact": {},
  "experience": [],
  "projects": [],
  "skills": [],
  "education": [],
  "certifications": [],
  "links": {}
}
```

### AI Usage

LLM is now used for structured extraction, parsing, and JSON conversion.

---

# Phase 2 — Deterministic ATS Analysis

## Objective

Evaluate all measurable aspects without using AI.

### Deliverables

* ATS formatting validation
* Section validation
* Resume length analysis
* Quantification detection
* Action verb detection
* Date validation
* Keyword extraction
* Duplicate skill detection
* Link validation
* GitHub link detection

### AI Usage

None.

---

# Phase 3 — Graph Engineering Foundation

## Objective

Build the orchestration layer.

### Deliverables

* LangGraph setup
* Shared ResumeState
* Graph routing
* Conditional execution
* Parallel execution
* Error handling
* Checkpointing

### Initial Graph

```text
START
   │
Resume Parser
   │
Planner
   │
END
```

---

# Phase 4 — Specialist AI Evaluators

## Objective

Replace monolithic prompting with specialized AI agents.

### Agents

* Experience Evaluator
* Project Evaluator
* Skills Evaluator
* Achievement Evaluator
* ATS Reviewer

Each evaluator receives only its relevant section and returns structured JSON.

---

# Phase 5 — Tool Binding

## Objective

Enable each AI evaluator to call specialized tools.

### Experience Agent

Tools

* Quantification Analyzer
* Action Verb Analyzer
* Employment Timeline Validator

### Project Agent

Tools

* GitHub Repository Fetcher
* Technology Extractor
* Architecture Detector

### ATS Agent

Tools

* Formatting Analyzer
* Keyword Analyzer
* Section Validator

### Principle

* Graph orchestrates workflow.
* LLM orchestrates tools.
* Tools execute deterministic tasks.

---

# Phase 6 — GitHub Intelligence

## Objective

Evaluate engineering quality through GitHub.

### Pipeline

GitHub URL

↓

Username Extraction

↓

GitHub API

↓

Repository Selection

↓

Repository Analysis

↓

Engineering Evaluation

### Evaluation Criteria

* Repository quality
* Documentation
* README
* Architecture
* Testing
* CI/CD
* Deployment
* Activity
* Engineering maturity

---

# Phase 7 — Intelligent Scoring Engine

## Objective

Aggregate specialist scores into a transparent final score.

### Weight Distribution

| Category                | Weight |
| ----------------------- | -----: |
| Experience              |    25% |
| Projects                |    25% |
| Skills                  |    15% |
| Quantified Achievements |    10% |
| GitHub                  |    10% |
| ATS Formatting          |     5% |
| Education               |     5% |
| Certifications          |     3% |
| Writing Quality         |     2% |

### Output

* Category scores
* Weighted overall score
* Confidence score
* Evidence
* Score explanations

---

# Phase 8 — Recommendation Engine

## Objective

Generate actionable resume improvements.

### Responsibilities

* Improve project descriptions
* Increase measurable impact
* Improve action verbs
* Suggest missing technologies
* Highlight engineering achievements
* Improve ATS compatibility

Recommendations should be prioritized by expected impact.

---

# Phase 9 — Hiring Decision Engine

## Objective

Produce a recruiter-friendly summary.

### Output

* Overall score
* Hiring recommendation
* Strengths
* Weaknesses
* Missing evidence
* Confidence score

Example recommendations:

* Strong Hire
* Hire
* Consider
* Needs Improvement

---

# Phase 10 — Advanced Intelligence

## Objective

Extend the platform with recruiter-focused capabilities.

### Planned Features

* Job Description ↔ Resume matching
* Role-specific scoring (Backend, AI, Frontend, DevOps, etc.)
* Recruiter-defined scoring weights
* Repository code analysis
* Portfolio website evaluation
* LinkedIn enrichment
* Multi-resume ranking
* Bias and fairness checks
* Interview question generation
* Personalized learning roadmap
* Analytics dashboard
* Historical benchmarking

---
