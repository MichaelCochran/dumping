# Lockheed Martin Innovation : View Submission

**URL:** https://lockheedmartin.brightidea.com/D27097

**Extracted:** 2026-07-28 15:28:00

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
- 2025Expert Finder(D27097)****
- ** Copy Link
- ** Report Abuse...
- ** Print
- ** Send to Project Room**Team Javanmardi, Caleb (US)**Promote1View Voters
Ambiguous job and team labels lead to employees wasting time searching for the right POC which is coupled in a time where systems engineering is on the rise​

​

Employee identifying metrics (expertise, licenses, location, etc.) are siloed in multiple systems (Enterprise WhitePages, Atlas, Service Central, etc.)​

​

Tracking down the right person delays project timelines, increases onboarding friction, and reduces productivity across the enterprise​
Attachments (2)**38651C92-817C-11F1-8DAC-0E70A83EB993.png48.83KBLM Fellas AIC 2026.pptx7.65MB**Organization / Team*LMFellasSolution Overview*
Query: input area of desired expertise, project bottlenecks, employee names​

﻿﻿Decipher: decodes acronyms before processing dataset ​

﻿﻿Enterprise WhitePages: provides data to map connections between employees to return relevant employees​

﻿﻿Enterprise Search: provides data about relevant employees that is not on WhitePages (i.e. patents)​

﻿﻿Output: who to contact to address your need; streamlined contact information​
Value Proposition*
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
Additional Information
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
Completed PowerPoint: Document Upload Certification*I certify that I have uploaded my completed PowerPoint presentation to the required folderlinked above.Link to Recorded Demo*https://lmco.sharepoint.us/sites/US-OneLM_AI_COE/_layouts/15/stream.aspx?id=%2Fsites%2FUS%2DOneLM%5FAI%5FCOE%2FShared%20Documents%2FAI%20Intern%20Challenge%2F2026%20AI%20Intern%20Challenge%2FSubmission%20Demo%20Recordings%2FLMFellasExpertFinder%2Emp4&referrer=StreamWebApp%2EWeb&referrerScenario=AddressBarCopied%2Eview%2E58daa54c%2D7091%2D488d%2Dae4e%2D47437e8a78d0
Please provide the name of the Genesis Organization for your Agent(s):*LMFellasPlease provide the Agent Name(s) as listed in Genesis:*
We used our own UI and repo in Gitlab to perform this task. However, a non API version exists as "Expert Finder"

﻿

﻿﻿https://gitlab.us.lmco.com/e472197/expertfinder﻿
Please certify that you have shared your Agent with the 2026 AI Intern Challenge Organization*YesI certify that I have not attached or included any unallowable information (such as Third Party Proprietary Information, Classified Information, or Export Controlled Information) in this submission:*YesComments (1)Comments (1)CAdd a commentDrag file(s) here*TTruncale, Mason (US)12 days ago *
- ** Copy Link
- ** Report Abuse...Wow. This is pretty cool! I know I would use this!
**ReplySubmitted07/17/2026StatusUnder ReviewStatsVote Score1Votes1Rank1Unique ViewsCRK16Total Views59Comments1Favorited0ProgressStage: EvaluationLinked IdeasNo linked Ideas