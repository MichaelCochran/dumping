# Project Specification: Spec To Sprint

**Project ID:** D27078  
**Team:** Hines, Aidan P (US)  
**Genesis Organization:** Spec-To-SprintAIC2026Owners  

---

## 1. Problem Statement

Most development teams consume a disproportionately large amount of time manually converting their technical specifications, designs, and other higher-level descriptions into specific and actionable Jira issues. This process is prone to errors and inconsistencies and delays the sprint process. The AI agent solves this problem by automatically reading the various technical specifications and creating relevant Jira issues, including acceptance criteria and the appropriate labels.

---

## 2. Solution Overview

The AI agent prototype serves as an intelligent intermediary between the MCP server connector and Lockheed Martin's Jira environment, extracting and safely ingesting live Jira metrics such as backlog health, sprint velocity, and issue status from the MCP feed for proper prioritization. Leveraging the Nemotron language model, the AI agent extracts relevant information from unstructured technical specifications, design documents, and user instructions to automatically create, update, or close Jira tickets with appropriate summary, description, acceptance criteria, story point, labeling, and assignees assignments along with linking references to the source documents, versions, and required classification tags. In addition to automatic creation of tickets, the agent can also parse, modify, and transition existing Jira issues for compliance with latest specifications and ongoing project progress; furthermore, the agent is capable of working in the interpret-on-demand mode allowing engineers to manually submit Jira requests for validation and execution to act as a fall-back for edge cases. The log of all the actions taken by the agent is being reported back to the MCP connector, thus creating a feedback mechanism for continuous model fine-tuning and improvement through metrics.

---

## 3. Value Proposition

The AI agent enables a drastic increase in speed from the time it takes to turn technical specifications and high-level directions into usable Jira stories and tasks. The process is made faster because the agent turns the lengthy process, which could take several hours, into something that happens in seconds. The agent makes sure that there is a consistent formatting, required fields, security tags, and traceability; therefore, there will be no missed acceptance criteria, inaccurate estimates, and duplication of stories. Reduction of mistakes made by humans enables engineers and program managers to focus more on design, testing, and integration of Jira stories and tasks, thus increasing productivity by 10-20 % per sprint. Linking of each story to its source document and including version metadata increases traceability. This solution is scalable as one model can be used in satellite, aircraft, missile, cyber, and other fields with slight adjustment of prompts. In total, these factors help save labor cost due to less manual ticket creation, decrease the amount of re-work related to bad stories, and provide a fast ROI of six months or less even for 50 person engineering team.

---

## 4. Technical Architecture

### AI Agents
- Spec-To-Sprint

### Technical Details
*No technical details provided*

---

## 5. Deliverables

- **Demo Recording:** https://lmco.sharepoint.us/sites/US-OneLM_AI_COE/_layouts/15/stream.aspx?sw=bypass&bypassReason=abandoned&id=%2Fsites%2FUS-OneLM_AI_COE%2FShared%20Documents%2FAI%20Intern%20Challenge%2F2026%20AI%20Intern%20Challenge%2FSubmission%20Demo%20Recordings%2Fspec_to_sprint_demo%2Emp4&startedResponseCatch=true&referrer=StreamWebApp%2EWeb&referrerScenario=AddressBarCopied%2Eview%2Eb7cdcd4a-b300-4d01-bf0f-839ea6dea5f4
- **PowerPoint:** See attachments folder
- **Genesis Organization:** Spec-To-SprintAIC2026Owners

---

## 6. Implementation Status

*Status information to be added*

---

## Specification Completeness: 90%

