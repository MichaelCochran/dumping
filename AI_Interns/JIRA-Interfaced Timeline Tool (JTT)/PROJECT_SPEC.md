# Project Specification: JIRA-Interfaced Timeline Tool (JTT)

**Project ID:** D27092  
**Team:** Janeja, Viraj (US)  
**Genesis Organization:** Team JTT AIC 2026  

---

## 1. Problem Statement

​Through our work supporting and supplementing the CTI team, we identified opportunities to improve efficiency in the managerial usage of JIRA.​ We noticed that JIRA tickets, capabilities, and related items can sometimes be tedious to locate or placed in hard-to-find areas.​ We also observed that JIRA does not always provide a highly visible workspace for key information, which can reduce clarity around: Deadlines, Changes, Status Updates. Alongside this, we identified a possible area for improvement in searching Confluence or JIRA for specific, relevant items.​ Our goal was to simplify this process by creating an easy-to-access and personalized program for spaces that would benefit from greater clarity​.

---

## 2. Solution Overview

Our solution took form in an AI brought material, and was achieved by creating a program revolving entirely around the users tokens and access reach, making it able to traverse a diverse landscape and have an incredible scope of usage. As opposed to the traditional agentic format, our application is built entirely standalone and without need for an external website, dramatically increasing the usage possibility, and potential growth. Our program does two things in particular: It collects tickets, entries of relevance (from both JIRA and confluence, as specified in the collection query), and available items, and consolidates them into a single viewable format. This format is additionally supported with supplemental features, such as diagrams, and JQL query metrics. Included is a tab with a direct agent connected to JIRA and Confluence, allowing for ease-of-query.​

​

---

## 3. Value Proposition

Our central value proposition for JTT is an improvement in overall efficiency and qualitative workspace supplementation. By introducing an easy-to-access feed displaying JIRA tickets, metrics, and an effectively AI-powered internal search engine, our agent/program should ideally be able to give clearer insight on projects from a high-level view, and additionally increase access to relevant confluence documents. For example, instead of searching through confluence for documents relating to topic 'xyz' for a particular solution, simply querying the AI feed for instructions tailored to the needs of the immediate fix would return highly relevant documentation, helpful advice, and possible fixes.﻿

---

## 4. Technical Architecture

### AI Agents
- JTT AIC 2026

### Technical Details
Our tool as opposed to regular agentic norms (via web) is built on a localized and personalized platform. Notably, this was something we cleared, and a distributable version can be found at the following gitlab: 
https://gitlab.us.lmco.com/e485374/jtt-distributable

Note**: There was an initial issue where no genesis agent was in place as the program could navigate from any genesis account, but there is now a forefront AI Factory agent in place that is utilized. (The agent has also been shared via organization)

Notably, we pull our LLM through genesis/AIFactory, utilizing the Lockheed Martin internally provided LLMs to act as the engine for our program.

Users are able to access an easy-to-use platform and enter their own tokens, allowing them to access their information specifically, and avoiding general security concerns. All query information, metric information, and platform information is stored locally via .json or .txt, with the exception of the secrets (tokens), which are stored via .env which is also listed in the .gitignore. 

On the backend side, we focused on implementing the system that gathers, organizes, and prepares workspace data for use across the application. We implemented logic to connect with JIRA and Confluence, process user-defined queries, retrieve relevant tickets and documentation, and consolidate that information into structured local outputs that the rest of the program can read from. Beyond simple collection, the backend also supports JQL based metric generation, status and deadline tracking, and the preparation of data for higher-level features such as diagrams, summaries, and AI-assisted search (all of which are implemented in the frontend). In this way, the backend acts as the engine of the tool and it turns scattered project information into organized, usable context for both the dashboard view and the internal query assistant.

---

## 5. Deliverables

- **Demo Recording:** https://lmco.sharepoint.us/sites/US-OneLM_AI_COE/_layouts/15/stream.aspx?id=%2Fsites%2FUS%2DOneLM%5FAI%5FCOE%2FShared%20Documents%2FAI%20Intern%20Challenge%2F2026%20AI%20Intern%20Challenge%2FSubmission%20Demo%20Recordings%2FViraj%20Janeja%2C%20Luke%20Shamaly%20AI%20Challenge%202026%2Emp4&referrer=StreamWebApp%2EWeb&referrerScenario=AddressBarCopied%2Eview%2E947be52e%2Dfa73%2D41e4%2Dabe9%2Db82ca4a87f63
- **PowerPoint:** See attachments folder
- **Genesis Organization:** Team JTT AIC 2026

---

## 6. Implementation Status

*Status information to be added*

---

## Specification Completeness: 100%

