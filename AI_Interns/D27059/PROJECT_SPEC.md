# Project Specification: Writer and Style Guide Manuals Agent

**Project ID:** D27059  
**Team:**   
**Genesis Organization:** Writer and Style Guide Manuals Agent  

---

## 1. Problem Statement

In Tech Pubs, writers frequently need to confirm the correct style, format, or grammar while marking up manuals. The official references for these decisions are the OMMS Style Guide (SMP 3233, ~112 pages) and the Writer's Guide (SMP 1771, ~64 pages), both provided only as PDF documents. The challenge, therefore, is to reduce the time and effort required for Tech Pubs writers to locate and understand the specific rules in SMP 3233 and SMP 1771 that apply to their current markup task.

---

## 2. Solution Overview

The assistant:

Retrieves relevant sections from the OMMS Style Guide (SMP 3233) and the Writer's Guide (SMP 1771),

Explain or summarize what they say,

Provide guidance on grammar, formatting, terminology, and style choices,

Avoid introducing rules, opinions, or content not supported by the manuals.

---

## 3. Value Proposition

Responds in under 1 minute.

If the manuals don't contain the answer, it replies: "I don't know based on the manuals provided."

If the request is out of scope, it replies: "That is out of my scope."

﻿﻿Tested with 32+ prompts, with answers and citations cross-checked against both manuals.

Reviewed by two Technical Publications Writers, who found it accurate and useful enough to adopt in daily work.

---

## 4. Technical Architecture

### AI Agents
- Writer and Style Guide Manuals Agent

### Technical Details
- ﻿Model: llama-4-scout﻿, which offers a large context window, image uploads, and AI Barrier mode compatibility.
- ﻿Temperature of 0.3 for more predictable answers.

---

## 5. Deliverables

- **Demo Recording:** https://lmco.sharepoint.us/:v:/r/sites/US-OneLM_AI_COE/Shared%20Documents/AI%20Intern%20Challenge/2026%20AI%20Intern%20Challenge/Submission%20Demo%20Recordings/Adrian_Carrasco_AI_Challenge_demo.mp4?csf=1&web=1&e=GPeSCy&nav=eyJyZWZlcnJhbEluZm8iOnsicmVmZXJyYWxBcHAiOiJTdHJlYW1XZWJBcHAiLCJyZWZlcnJhbFZpZXciOiJTaGFyZURpYWxvZy1MaW5rIiwicmVmZXJyYWxBcHBQbGF0Zm9ybSI6IldlYiIsInJlZmVycmFsTW9kZSI6InZpZXcifX0%3D
- **PowerPoint:** See attachments folder
- **Genesis Organization:** Writer and Style Guide Manuals Agent

---

## 6. Implementation Status

*Status information to be added*

---

## Specification Completeness: 90%

