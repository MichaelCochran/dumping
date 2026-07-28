# Project Specification: Expert Finder

**Project ID:** D27097  
**Team:** Javanmardi, Caleb (US)  
**Genesis Organization:** LMFellas  

---

## 1. Problem Statement

Ambiguous job and team labels lead to employees wasting time searching for the right POC which is coupled in a time where systems engineering is on the rise​ ​ Employee identifying metrics (expertise, licenses, location, etc.) are siloed in multiple systems (Enterprise WhitePages, Atlas, Service Central, etc.)​ ​ Tracking down the right person delays project timelines, increases onboarding friction, and reduces productivity across the enterprise​

---

## 2. Solution Overview

Query: input area of desired expertise, project bottlenecks, employee names​

﻿﻿Decipher: decodes acronyms before processing dataset ​

﻿﻿Enterprise WhitePages: provides data to map connections between employees to return relevant employees​

﻿﻿Enterprise Search: provides data about relevant employees that is not on WhitePages (i.e. patents)​

﻿﻿Output: who to contact to address your need; streamlined contact information​

---

## 3. Value Proposition

Estimate​

​

Speed & Efficiency​

    Search time: 45 min → 7 min ​

    First‑try success: 48 % → 84 % ​

Cost Savings​

    ≈ 4 person‑hours/yr saved → ~ $10 mil/yr (conservative)​

    Coverage & Accuracy​

AI‑enriched knowledge graph covers 99 % of 141 k employee records (144,000 rows in CSV, 8 million unique data points)​

    Strategic Benefits​

    Breaks knowledge silos & promotes cross‑domain collaboration​

    ROI Snapshot (12 mo)​

    Total benefit ≈ $240 k​

    Implementation cost ≈ $30 k​

    Net gain ≈ $210 k saved/yr ROM​

​

﻿﻿Actual​

​

Job Completion​

   In some roles, 90% of the job is knowing who to action for problems​

    Our working tool will help alleviate connection issues across platforms​

Future​

    Utilize MyAccess API, "Professional: Job Descriptions" in WhitePages ​

    Train model on key words and job classifications for greater search accuracy across business areas and programs​

Keep live data on new hires, retirees, and shifts in employment​

​

---

## 4. Technical Architecture

### AI Agents
- We used our own UI and repo in Gitlab to perform this task. However, a non API version exists as "Expert Finder"

### Technical Details
AI Models & LLMs​

Genesis AI (Lockheed Martin LLM platform) - nemotron-3-super-120b-a12b model for candidate recommendations and query interpretation​﻿﻿

Temperature: 0.2 (deterministic), Max tokens: 1500, Timeout: 30s​

Data Sources​

Employee CSV: 141,000+ records with 40+ searchable columns (skills, expertise, projects, certifications, biography)​

Knowledge Base: SQLite database with 20+ LM programs (F-35, THAAD, etc.) - program metadata, locations, departments​

Analytics DB: SQLite tracking for queries, views, filters, response times​

Data Formats​

Input: CSV (UTF-8), JSON (API responses), Environment variables (.env)​

Output: JSON (structured ranked candidates with evidence), HTML (web UI), Plain text (CLI)​

﻿

﻿﻿Integrations​

Genesis AI (Required): LLM recommendations via chat completions API​

Decipher API (Optional, disabled): Query expansion with 7-term limit​

Enterprise Search (Optional, disabled): OAuth2-based internal knowledge enrichment​

Google Scholar (Optional, disabled): External domain intelligence with circuit breaker​

Key Features​

Multi-phase ranking: filtering → text matching → scoring → enrichment | Intent classification & service routing​

Geographic radius search (Haversine) | Evidence-based explainability | Knowledge web visualization​

Fallback mechanisms | GitLab CI/CD pipeline | Performance: <5s typical response, in-memory operations​

Core Technologies​

Backend: Python 3.8+, Flask 3.0+ | Data Processing: Pandas 2.2+, FuzzyWuzzy, Levenshtein distance​

​

​

---

## 5. Deliverables

- **Demo Recording:** *Not provided*
- **PowerPoint:** See attachments folder
- **Genesis Organization:** LMFellas

---

## 6. Implementation Status

*Status information to be added*

---

## Specification Completeness: 100%

