
# Guiding Principles

* Prefer deterministic logic whenever possible.
* Use AI only for reasoning and qualitative evaluation.
* Keep scoring explainable and reproducible.
* Make every evaluation traceable to supporting evidence.
* Design each graph node to have a single responsibility.
* Bind only the tools required by each specialist agent.
* Keep the graph modular, testable, and extensible.
* Build components that can be independently improved without affecting the overall workflow.

---

# High-Level Architecture

```text
Resume
   │
   ▼
Parser
   │
   ▼
Planner
   │
   ├──────────────┬──────────────┬──────────────┐
   ▼              ▼              ▼              ▼
Experience     Projects       Skills        ATS Review
Agent          Agent          Agent         Agent
   │              │              │              │
 Tool Calls    Tool Calls    Tool Calls    Tool Calls
   └──────────────┴──────────────┴──────────────┘
                     │
                     ▼
              GitHub Intelligence
                     │
                     ▼
              Score Aggregator
                     │
                     ▼
          Recommendation Engine
                     │
                     ▼
             Hiring Decision Engine
                     │
                     ▼
                    END
```
