# Project Specification: Fortify++

**Project ID:** D27066  
**Team:** Van Beck, Chad F (US)  
**Genesis Organization:** FortifyPlusPlusAIC2026  

---

## 1. Problem Statement

Security teams at Lockheed Martin rely on Fortify Static Application Security Testing (SAST) to scan large C++ codebases for potential vulnerabilities. These scans can generate hundreds or thousands of findings per project, and a substantial portion are ultimately determined to be non‑issues or false positives. Today, security analysts must manually review each finding, locate the relevant source code, interpret Fortify's rule description, and coordinate with developers when the context is unclear. For a typical project, this review work can take many days or even weeks of focused analyst time. This manual process slows down the path from scan to release, consumes scarce expert capacity, and makes it harder to concentrate on the smaller set of findings that truly represent security risk. There is a need for an internal AI‑assisted solution that can help separate likely false positives from likely real issues, while keeping analysts in control of final decisions.

---

## 2. Solution Overview

Fortify++ is an AI‑assisted analysis tool that works on top of existing Fortify scans. It ingests Fortify report artifacts (such as .fpr, CSV, or PDF), pulls the related source‑code snippets from the Git repository, and uses Genesis to classify each finding as likely true issue, likely false positive, or needs review.

The prototype includes:

- A simple web UI for uploading Fortify reports and starting an analysis
- A back‑end service that parses findings and retrieves the matching code context
- An AI classification step using Genesis, with confidence indicators
- An interactive results dashboard with filters and summary charts
- Export options (CSV, JSON, PDF/Markdown) for sharing results or attaching to existing review workflows
The design preserves current Fortify and GitLab CI/CD workflows while adding an AI‑based layer to help analysts quickly understand and organize scan output.

---

## 3. Value Proposition

Fortify++ has the potential to deliver significant time and cost savings for Lockheed Martin cyber teams.

Today, reviewing a single Fortify scan can require over 200 hours of manual analyst effort. In our prototype evaluation, using AI to pre-classify findings reduced the manual review workload to roughly 10–20 hours per project, while still keeping analysts in control of final decisions.

Using a fully loaded analyst cost of about $150,000 per year (approximately $72 per hour):

Per project:

- Time saved is roughly 180 hours
- Cost impact is approximately 180 × $72 ≈ $13,000 saved per project
Ongoing false-positive review:

- Avoiding re-checking about 100 false positives per month (around 30 minutes each) saves about 50 hours
- Cost impact is about 50 × $72 ≈ $3,600 per month, or roughly $43,000 per year for each team using Fortify++
By automatically flagging likely false positives and highlighting items that merit closer review, Fortify++ helps free up expert time, shorten the cycle from scan to release decision, and scale security reviews across more projects without a proportional increase in analyst cost.

---

## 4. Technical Architecture

### AI Agents
- FortifyPlusPlus

### Technical Details
- Built on Lockheed Martin's internal Genesis LLM platform and LMNavigator components
- Integrates with existing GitLab CI/CD pipelines that already produce Fortify .fpr artifacts
- Uses Fortify CLI tools and Git repository access to extract findings and code context
- All processing stays within Lockheed Martin's internal network; no external models or services are used
- Initial focus is on C++ codebases, with a path to extend to other languages and tools.
- Designed so that AI output is advisory: security analysts remain the final decision‑makers on whether a finding is accepted, rejected, or escalated

---

## 5. Deliverables

- **Demo Recording:** https://lmco.sharepoint.us/:v:/s/US-OneLM_AI_COE/IQAuwrnzeB_rQqXvoNfVEw91AT7JTlidDHJayKJ_5RF1l3c?e=jJ5AIb
- **PowerPoint:** See attachments folder
- **Genesis Organization:** FortifyPlusPlusAIC2026

---

## 6. Implementation Status

*Status information to be added*

---

## Specification Completeness: 100%

