# Project Specification: ARES: Automated Reconciliation and Evidence for STIGs

**Project ID:** D27101  
**Team:** Di Domizio, Roman (US)  
**Genesis Organization:** ARES - AI Intern Challenge  

---

## 1. Problem Statement

During STIG compliance validation on NGG's 1000+ unclassified systems, cyber engineers use multiple automated scanners as required to meet deadlines and defense-in-depth principles. However, these tools frequently produce conflicting results. Our validation found 41 disagreements (11.2% of checks) and 20 gaps where neither tool could automate the check. Each disagreement requires manual reconciliation: SSHing into the target system, running validation commands, interpreting outputs, and determining ground truth. This process takes 3-4+ hours per system and requires deep STIG expertise. With 1000+ NGG systems requiring 2-3 validation cycles per year, manual reconciliation consumes over 3,500 hours per cycle, equivalent to 87 weeks of full-time work. ARES (Automated Reconciliation and Evidence for STIGs) solves this by using FOUR AI agents that autonomously SSH into target systems and execute validation commands to reconcile conflicting scanner outputs and fill coverage gaps. The system reduces reconciliation time from 3,500+ hours to 500-750 hours per cycle, freeing 2.6-4.3 full-time cyber engineers for high-value security work while eliminating critical false negatives through multi-source validation.

---

## 2. Solution Overview

ARES (Automated Reconciliation and Evidence for STIGs) is a multi-agent AI system that autonomously reconciles STIG scanner outputs through direct CLI validation on target systems. Unlike traditional scanners that only report findings, ARES agents SSH into target systems and execute actual validation commands to determine ground truth. The system uses FOUR Genesis AI Factory agents orchestrated through a custom Streamlit UI: Parser Agent normalizes multiple scanner outputs via MCP tools, Gap Coverage Agent validates findings neither scanner automated, Determination Agent resolves all disagreements through exhaustive CLI validation, and Reporting Agent generates reconciled CKL files with comprehensive metrics and POA&M comments. Agents use a multi-command verification strategy, iteratively running additional validation commands when confidence is below 80%, only escalating to humans after exhausting all verification options.

---

## 3. Value Proposition

For NGG's 1000+ unclassified systems, ARES reduces reconciliation from 3,500+ hours to 500-750 hours per validation cycle, saving 2,750-3,000 hours per cycle. This frees 2.6-4.3 full-time cyber engineers year-round for high-value security work, delivering $286K-473K in annual cost savings. The system eliminates CAT I false negatives through multi-source validation, ensures repeatable and auditable results through deterministic CLI validation, and automatically generates POA&M comments and remediation recommendations. The architecture supports future expansion to classified systems, Windows, and other platforms beyond RHEL 8. Because it deploys on unclassified networks, ARES demonstrates value immediately without classified accreditation delays. This transforms STIG validation from a manual bottleneck to automated quality control, enabling cyber teams to focus on threat hunting, vulnerability management, and security architecture.

---

## 4. Technical Architecture

### AI Agents
- ARES Parser Agent AIC 2026
- ARES Reporting Agent AIC 2026
- ARES Determination Agent AIC 2026
- ARES Gap Coverage Agent AIC 2026

### Technical Details
ARES uses Genesis AI Factory with the nemotron-3-ultra-550b-a55b model and FastMCP v1.3.0 deployed to PCell OpenShift for tool integration. We built a custom Streamlit UI for multi-agent orchestration because LM Navigator only supports one agent at a time and would not work for this complex workflow requiring sequential data passing between four agents. The system implements read-only SSH access with command validation, comprehensive audit logging, and limited user permissions for security. The current prototype targets RHEL 8 systems (366 STIG rules) but the architecture is designed for Windows and other platforms. The deployment strategy starts with unclassified NGG systems to demonstrate value immediately, then expands to classified systems after proving the concept. The modular design makes it easy to add new scanner tools like OpenSCAP and Nessus. This is not another STIG scanner but a meta-validator that sits above all scanners, using AI reasoning plus autonomous CLI access to determine ground truth when tools disagree. The Parser Agent, Gap Coverage Agent, Determination Agent, and CLI executor all work exactly as planned. The Reporting Agent is functional but not entirely complete and needs improvement for production use. Development took 14 days (July 2-16, 2026), demonstrating feasibility for rapid enterprise AI deployment.

---

## 5. Deliverables

- **Demo Recording:** https://lmco.sharepoint.us/:v:/s/US-OneLM_AI_COE/IQAnzK5ABNYoQ42g48ZWDU8_AYVZqd6e8KhFe8yJ4KuEIeY?e=TsCTe0
- **PowerPoint:** See attachments folder
- **Genesis Organization:** ARES - AI Intern Challenge

---

## 6. Implementation Status

*Status information to be added*

---

## Specification Completeness: 100%

