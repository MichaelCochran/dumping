# Lockheed Martin Innovation : View Submission

**URL:** https://lockheedmartin.brightidea.com/D27080

**Extracted:** 2026-07-28 15:36:23

---

Lockheed Martin Innovation : View Submission

- 
- 
- 

- 
 
- 
 
- 

 Skip to main content** Search **
## Notifications
**No NotificationsMark All as Read**
## Action Items
**No Action ItemsView All**CC**Cochran, Michael (US)michael.cochran@lmco.com
- **Home
- **Profile
- **Explore Apps
- **Log Out
- *
- HOME
- BROWSE SUBMISSIONS
- FAQ
- PROJECT ARCHIVE*
- 2024
- 2025
- *
- HOME
- BROWSE SUBMISSIONS
- FAQ
- PROJECT ARCHIVE*
- 2024
- 2025Jira Sprint Tracker Agent(D27080)****
- ** Copy Link
- ** Report Abuse...
- ** Print
- ** Send to Project Room**Team Vernekar, Kedar S (US)**Promote1View Voters
Many teams waste valuable time due to poor sprint execution that stems from lack of visibility at every phase of the sprint lifecycle: planning, execution, and reflection.​ Before the sprint, ﻿teams start sprints over-committed, with stories missing estimates, no acceptance criteria, and entire categories of work (testing, security, observability, etc.) absent from the plan.​ ﻿During the sprint, blocked stories go unnoticed for days. Nobody realizes the team is off-track until standup, or worse, until the sprint ends. ﻿Retrospectives done after the sprint rely on memory. Teams cannot quantify what went wrong or identify patterns across sprints. ﻿The result of all this is that there is preventable rework, missed deadlines, and developers spending time on Jira management instead of building software.
Attachments (2)**715E4910-8159-11F1-8DAC-0E70A83EB993.png123.05KB2026 AIC friscofans Jira Sprint Tracker Agent.pptx583.98KB**Organization / Team*friscofansSolution Overview*
Our solution to this problem is ﻿a Genesis-powered AI Agent and MCP server that provides visibility across the entire sprint lifecycle, tracking sprints and catching blind spots before they become problems and giving teams data-driven insights at every phase. Before the sprint, the AI agent can ﻿analyze upcoming sprints for coverage gaps (testing, security, documentation, etc.), stories missing estimates or acceptance criteria, and over/under-commitment vs. expected velocity. During the sprint, the agent can ﻿monitor progress in real-time, flag blocked stories, and compare completion percentage vs. time elapsed to detect off-track sprints early. Finally, at the end of the sprint, the agent can ﻿generate quick retrospectives with committed vs. completed metrics, carry-over analysis, and actionable improvement suggestions. The agent also has the ability to ﻿create, update, and move issues with human-in-the-loop approval and fill gaps identified by analysis without leaving the conversation. This agent's intended audience is anyone that can use Jira.
Value Proposition*
The quantitative impacts this agent provides are enormous. Sprint planning preparation and blind spot checking takes an average of 20 minutes and may not catch all gaps, while this agent can do all of that in under 2 minutes and catch a lot more gaps. Additionally, the AI model will be able to catch blocked stories instantly, while it may take a couple of days for employees to catch it. Retrospective creation is also quicker, with the AI model taking under 2 minutes compared to a typical employee taking around 20 minutes to create one. Some of the qualitative benefits of this agent include overcommitment prevention, catching missing coverage, and the usage of a human-in-the-loop so that AI suggestions are correctly validated.
Additional Information
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
Completed PowerPoint: Document Upload Certification*I certify that I have uploaded my completed PowerPoint presentation to the required folderlinked above.Link to Recorded Demo*https://lmco.sharepoint.us/:v:/s/US-OneLM_AI_COE/IQAqCQM2XgW7S7QqNL2fiDBFAadqapLxyT66chvJN7SXKy4?e=dQ5X7r&nav=eyJyZWZlcnJhbEluZm8iOnsicmVmZXJyYWxBcHAiOiJTdHJlYW1XZWJBcHAiLCJyZWZlcnJhbFZpZXciOiJTaGFyZURpYWxvZy1MaW5rIiwicmVmZXJyYWxBcHBQbGF0Zm9ybSI6IldlYiIsInJlZmVycmFsTW9kZSI6InZpZXcifX0%3DPlease provide the name of the Genesis Organization for your Agent(s):*friscofansPlease provide the Agent Name(s) as listed in Genesis:*
Jira Sprint Tracker Agent - AIC 2026
Please certify that you have shared your Agent with the 2026 AI Intern Challenge Organization*YesI certify that I have not attached or included any unallowable information (such as Third Party Proprietary Information, Classified Information, or Export Controlled Information) in this submission:*YesComments (0)Comments (0)CAdd a commentDrag file(s) hereNo commentsSubmitted07/16/2026StatusUnder ReviewStatsVote Score1Votes1Rank1Unique ViewsUHD12Total Views33Comments0Favorited0ProgressStage: EvaluationLinked IdeasNo linked Ideas