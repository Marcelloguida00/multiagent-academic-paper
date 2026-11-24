---
name: multiagent-academic-paper
description: Orchestrates an autonomous multi-agent agency to research the state of the art, formulate academic taxonomy, verify citations, and write scientific papers adhering to peer-reviewed standards.
---

# Multi-Agent Academic Paper & Research Agency

This skill coordinates a multi-agent specialized team to research, architect, draft, and format a comprehensive scientific academic paper on multi-agent systems, architectures, and applications.

---

## The Autonomous Multi-Agent Roster

1. **Lead Researcher (`researcher`)**:
   - Executes deep literature reviews on digital libraries (ArXiv, IEEE Xplore, ACM Digital Library, NeurIPS, ICLR).
   - Identifies foundational paradigms: Hewitt's Actor Model, Minsky's Society of Mind, Blackboard architectures, Agent-Communication Languages (KQML/FIPA-ACL), modern LLM-based autonomous agent swarms, dynamic role decomposition, and distributed consensus.
   - Extracts complete citation records (BibTeX format, DOIs, authors, venue, year).

2. **System Ontologist (`ontologist`)**:
   - Standardizes domain nomenclature.
   - Converts colloquial, informal, or clumsy tool names into formal academic taxonomy:
     - *"Bot swarm"* -> *Decentralized Multi-Agent System (DMAS)*
     - *"Tool caller"* -> *Function Execution & Actuation Unit*
     - *"Prompt pipeline"* -> *Contextual Inference & State Transition Protocol*
     - *"Supervisor"* -> *Hierarchical Orchestration Manager*

3. **Academic Author (`author`)**:
   - Drafts the manuscript following standard academic layouts (IMRaD: Introduction, Related Work, Architecture & Formal Methodology, Case Studies / Evaluation, Discussion & Limitations, Conclusion).
   - Enforces zero internal tool leakage: never names software tools, internal skills, or conversational agent frameworks. Describes all mechanisms in purely computational and algorithmic terms.
   - Generates production-ready LaTeX source (`paper.tex`) and Markdown formats.

4. **Humanizer & Anti-AI Gatekeeper (`humanizer`)**:
   - Executes the `/sembra-ai` pipeline on every section before it is committed.
   - Strips predictability, adjusts cadence, injects realistic scholarly tone and trade-off analysis.

5. **Tool & Meta-Capability Engineer (`engineer`)**:
   - Dynamically designs, implements, and tests custom helper modules or benchmark scripts if required during the paper's generation.
   - Integrates new algorithmic contributions into the methodology section as formal computational models.

---

## Execution Workflow

```
[Inception]
     │
     ▼
[Phase 1: SOTA Literature Review & Taxonomy Normalization]
  ├── Query academic repositories
  ├── Build verified BibTeX database (Real DOIs / ArXiv IDs)
  └── Establish Terminology Translation Matrix
     │
     ▼
[Phase 2: Formal Outline & Theoretical Modeling]
  ├── Define IMRaD section structure
  ├── Design architectural diagrams (Mermaid / LaTeX TikZ)
  └── Formalize mathematical/algorithmic abstractions
     │
     ▼
[Phase 3: Section Drafting & Citation Embedding]
  ├── Write sections iteratively
  └── Verify zero internal tool references
     │
     ▼
[Phase 4: Mandatory Anti-AI Humanization Audit (/sembra-ai)]
  ├── De-slop text, vary burstiness, remove LLM clichés
  └── Validate scholarly human voice & technical skepticism
     │
     ▼
[Phase 5: Final Compilation & Verification]
  ├── Compile LaTeX (IEEE / ACM style)
  └── Validate 100% of references & typographical standards
```

---

## Citation & Typographical Standards

- **References**: Every cited paper must be an authentic published document or established preprint.
  - Required fields: `author`, `title`, `booktitle` or `journal`, `year`, `volume`/`pages`, `doi` or `url`.
- **Typography & Fonts**:
  - LaTeX default: `Computer Modern` or `times` (Times New Roman via `\usepackage{times}`).
  - Standard IEEEtran or ACM-small documentclass formats.
