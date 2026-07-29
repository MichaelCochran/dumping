# Project Specification: Jira Sprint Tracker Agent

**Project ID:** D27080  
**Team:** Vernekar, Kedar S (US)  
**Genesis Organization:** friscofans  

---

## 1. Problem Statement

Many teams waste valuable time due to poor sprint execution that stems from lack of visibility at every phase of the sprint lifecycle: planning, execution, and reflection.​ Before the sprint, ﻿teams start sprints over-committed, with stories missing estimates, no acceptance criteria, and entire categories of work (testing, security, observability, etc.) absent from the plan.​ ﻿During the sprint, blocked stories go unnoticed for days. Nobody realizes the team is off-track until standup, or worse, until the sprint ends. ﻿Retrospectives done after the sprint rely on memory. Teams cannot quantify what went wrong or identify patterns across sprints. ﻿The result of all this is that there is preventable rework, missed deadlines, and developers spending time on Jira management instead of building software.

---

## 2. Solution Overview

Our solution to this problem is ﻿a Genesis-powered AI Agent and MCP server that provides visibility across the entire sprint lifecycle, tracking sprints and catching blind spots before they become problems and giving teams data-driven insights at every phase. Before the sprint, the AI agent can ﻿analyze upcoming sprints for coverage gaps (testing, security, documentation, etc.), stories missing estimates or acceptance criteria, and over/under-commitment vs. expected velocity. During the sprint, the agent can ﻿monitor progress in real-time, flag blocked stories, and compare completion percentage vs. time elapsed to detect off-track sprints early. Finally, at the end of the sprint, the agent can ﻿generate quick retrospectives with committed vs. completed metrics, carry-over analysis, and actionable improvement suggestions. The agent also has the ability to ﻿create, update, and move issues with human-in-the-loop approval and fill gaps identified by analysis without leaving the conversation. This agent's intended audience is anyone that can use Jira.

---

## 3. Value Proposition

The quantitative impacts this agent provides are enormous. Sprint planning preparation and blind spot checking takes an average of 20 minutes and may not catch all gaps, while this agent can do all of that in under 2 minutes and catch a lot more gaps. Additionally, the AI model will be able to catch blocked stories instantly, while it may take a couple of days for employees to catch it. Retrospective creation is also quicker, with the AI model taking under 2 minutes compared to a typical employee taking around 20 minutes to create one. Some of the qualitative benefits of this agent include overcommitment prevention, catching missing coverage, and the usage of a human-in-the-loop so that AI suggestions are correctly validated.

---

## 4. Technical Architecture

### AI Agents
- Jira Sprint Tracker Agent - AIC 2026

### Technical Details
**Stack & Architecture:​**

• Python 3.11 + FastMCP (Model Context Protocol framework)​

• Async HTTP via httpx to Jira Agile REST API v2​

**Deployment:​**

• Podman container (daemonless/rootless) → GitLab CI → Knative Serving on Kubernetes​

• Hosted on LM AI Factory platform (PCell OpenShift), discovered via Genesis Connector Catalog​

**Security & Data:​**

• Jira PAT provided per-session, stored only in memory, never persisted​

• All created issues auto-tagged 'ai-drafted' for auditability​

• No sensitive data sent to model; only issue text and sprint metadata​﻿

**Quality Guardrails:​**

• Self-scores every drafted issue against a deterministic rubric (verb-first summary, AC specificity, edge-case coverage) before presenting to the user.​

**Duplicate detection:** ​

• Checks existing backlog for potential duplicates before creating new issues​

**26 MCP tools spanning discovery, analysis, validation, and issue management​**

---

## 5. Deliverables

- **Demo Recording:** https://lmco.sharepoint.us/:v:/s/US-OneLM_AI_COE/IQAqCQM2XgW7S7QqNL2fiDBFAadqapLxyT66chvJN7SXKy4?e=dQ5X7r&nav=eyJyZWZlcnJhbEluZm8iOnsicmVmZXJyYWxBcHAiOiJTdHJlYW1XZWJBcHAiLCJyZWZlcnJhbFZpZXciOiJTaGFyZURpYWxvZy1MaW5rIiwicmVmZXJyYWxBcHBQbGF0Zm9ybSI6IldlYiIsInJlZmVycmFsTW9kZSI6InZpZXcifX0%3D
- **PowerPoint:** See attachments folder
- **Genesis Organization:** friscofans

---

## 6. Implementation Status

*Status information to be added*

---

## Specification Completeness: 100%

