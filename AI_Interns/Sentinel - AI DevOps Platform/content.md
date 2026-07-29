# Lockheed Martin Innovation : View Submission

**URL:** https://lockheedmartin.brightidea.com/D27065

**Extracted:** 2026-07-28 15:39:13

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
- 2025Sentinel: AI DevOps Platform(D27065)****
- ** Copy Link
- ** Report Abuse...
- ** Print
- ** Send to Project Room*Ronit Chattaraj*Promote1View Voters
• Developers waste significant time switching between 4+ disconnected systems (GitLab, Confluence, Jira, Fortify) to complete a single task

• Diagnosing a pipeline failure requires: opening GitLab, finding the failed job, reading logs, downloading SAST artifacts, parsing JSON files, then cross-referencing with code, which is a 10-15 minute manual process per incident

• Understanding a new ticket requires: reading Jira, searching Confluence for documentation, finding relevant code, and asking teammates who the expert is, context that's scattered across multiple tabs

• Security vulnerability remediation requires: reading Fortify scan results, locating the vulnerable code, understanding the fix, then committing and opening a merge request: a multi-step workflow across systems

• New developer onboarding takes days just to navigate the ecosystem and understand who owns what

• There is no unified interface that connects code, documentation, tickets, and security findings into one searchable, actionable system

• This problem affects every software engineering team at Lockheed Martin that uses GitLab, Confluence, and Jira
Attachments (2)**7E5DBD6C-8121-11F1-8DAC-0E70A83EB993.png89.84KB2026 AI Intern Challenge Presentation - Ronit Chattaraj (Final).pptx11.82MB**Organization / Team*Team Sentinel AIC 2026Solution Overview*
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

Value Proposition*
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

Additional InformationNo answerCompleted PowerPoint: Document Upload Certification*I certify that I have uploaded my completed PowerPoint presentation to the required folderlinked above.Link to Recorded Demo*https://lmco-my.sharepoint.us/:v:/g/personal/e484193_us_lmco_com/IQAR9XtL6CtwRYvTHCvi8dNPAc2CZDlYkqO4e8Y5AoWhE9I?e=Bbjvho&nav=eyJyZWZlcnJhbEluZm8iOnsicmVmZXJyYWxBcHAiOiJTdHJlYW1XZWJBcHAiLCJyZWZlcnJhbFZpZXciOiJTaGFyZURpYWxvZy1MaW5rIiwicmVmZXJyYWxBcHBQbGF0Zm9ybSI6IldlYiIsInJlZmVycmFsTW9kZSI6InZpZXcifX0%3DPlease provide the name of the Genesis Organization for your Agent(s):*e484193-us-lmco.com, shared with Team Sentinel AIC 2026 (access point)Please provide the Agent Name(s) as listed in Genesis:*
Sentinel AIC 2026 - Final Submission
Please certify that you have shared your Agent with the 2026 AI Intern Challenge Organization*YesI certify that I have not attached or included any unallowable information (such as Third Party Proprietary Information, Classified Information, or Export Controlled Information) in this submission:*YesComments (1)Comments (1)CAdd a commentDrag file(s) here*Ronit Chattaraj12 days ago *
- ** Copy Link
- ** Report Abuse...Just to note: there is an additional tool, confluence generic search without specific ID, that usually works, I believe over the last few days due to maintenance/upgrades some functionality has broken - I know other interns have had the same problem.
**ReplySubmitted07/16/2026StatusUnder ReviewStatsVote Score1Votes1Rank1Unique ViewsNMR23Total Views79Comments1Favorited2ProgressStage: EvaluationLinked IdeasNo linked Ideas