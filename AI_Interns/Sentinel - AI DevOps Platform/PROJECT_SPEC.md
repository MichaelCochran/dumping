# Project Specification: Sentinel: AI DevOps Platform

**Project ID:** D27065  
**Team:**   
**Genesis Organization:** e484193-us-lmco.com, shared with Team Sentinel AIC 2026 (access point)  

---

## 1. Problem Statement

• Developers waste significant time switching between 4+ disconnected systems (GitLab, Confluence, Jira, Fortify) to complete a single task • Diagnosing a pipeline failure requires: opening GitLab, finding the failed job, reading logs, downloading SAST artifacts, parsing JSON files, then cross-referencing with code, which is a 10-15 minute manual process per incident • Understanding a new ticket requires: reading Jira, searching Confluence for documentation, finding relevant code, and asking teammates who the expert is, context that's scattered across multiple tabs • Security vulnerability remediation requires: reading Fortify scan results, locating the vulnerable code, understanding the fix, then committing and opening a merge request: a multi-step workflow across systems • New developer onboarding takes days just to navigate the ecosystem and understand who owns what • There is no unified interface that connects code, documentation, tickets, and security findings into one searchable, actionable system • This problem affects every software engineering team at Lockheed Martin that uses GitLab, Confluence, and Jira

---

## 2. Solution Overview

Sentinel is an AI DevOps Platform with 20 MCP tools that connects to GitLab, Confluence, Jira, and Fortify SAST through a single natural language interface deployed on LM Navigator.

**Key Features:**

• Cross-system synthesis — one question pulls live data from multiple enterprise systems simultaneously and returns one unified answer

• Pipeline diagnostics — automatically identifies failed jobs, extracts error patterns, downloads and parses Fortify/Semgrep SAST artifacts to surface exact vulnerabilities with file paths and line numbers

• Confluence documentation access — reads and synthesizes architecture docs, process guides, and team knowledge from 800+ pages

• Jira integration — retrieves ticket details, searches by keyword, shows your assignments and status

• Expert finding — analyzes 90-day commit history to identify who currently owns specific areas of the codebase

• Impact analysis — before you change a file, shows what depends on it, related tests, and risk level

• Autonomous code repair — reads vulnerable code, writes a secure fix, commits it to a new branch in GitLab, and triggers the CI pipeline automatically

• Deployed serverless on Kubernetes (Knative) with automated CI/CD, registered Online in the Genesis AI Factory connector catalog﻿

---

## 3. Value Proposition

**Time Savings:**

• Pipeline diagnosis reduced from 10-15 minutes of manual investigation to a single question answered in seconds

• New developer onboarding context (understanding tickets, finding code, identifying experts) compressed from hours of clicking between systems to one synthesized response

• Security vulnerability remediation streamlined — Sentinel reads the finding, locates the code, writes the fix, and commits it autonomously

**Scalability & Adoption:**

• Every software engineering team at Lockheed Martin already uses GitLab, Confluence, Jira, and Fortify — Sentinel plugs into all four with no new tools to learn

• Multi-tenancy requires only a configuration change (GitLab group ID, Confluence space key, Jira project key) — any team can onboard in minutes

• Already deployed and registered Online in the Genesis AI Factory connector catalog — available for immediate use through Navigator

**Competitive Advantage:**

• This is not a prototype — it is production-deployed on Kubernetes and I use it daily for my own tickets on the Competitive Intelligence Hub team﻿

• Every response is grounded in live API calls to real systems — no hallucinated or outdated information﻿

---

## 4. Technical Architecture

### AI Agents
- Sentinel AIC 2026 - Final Submission

### Technical Details
*No technical details provided*

---

## 5. Deliverables

- **Demo Recording:** https://lmco-my.sharepoint.us/:v:/g/personal/e484193_us_lmco_com/IQAR9XtL6CtwRYvTHCvi8dNPAc2CZDlYkqO4e8Y5AoWhE9I?e=Bbjvho&nav=eyJyZWZlcnJhbEluZm8iOnsicmVmZXJyYWxBcHAiOiJTdHJlYW1XZWJBcHAiLCJyZWZlcnJhbFZpZXciOiJTaGFyZURpYWxvZy1MaW5rIiwicmVmZXJyYWxBcHBQbGF0Zm9ybSI6IldlYiIsInJlZmVycmFsTW9kZSI6InZpZXcifX0%3D
- **PowerPoint:** See attachments folder
- **Genesis Organization:** e484193-us-lmco.com, shared with Team Sentinel AIC 2026 (access point)

---

## 6. Implementation Status

*Status information to be added*

---

## Specification Completeness: 80%

