"""
Generate project specifications from extracted Brightidea content
"""

import re
import json
from pathlib import Path
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

BASE_DIR = Path(__file__).parent
INCOMPLETE_LIST_FILE = BASE_DIR / "projects_needing_detail.md"

def extract_project_info(content_md_text, page_id):
    """Extract key project information from markdown content"""
    
    project = {
        "id": page_id,
        "title": "",
        "team": "",
        "problem": "",
        "solution": "",
        "value": "",
        "technical_details": "",
        "agents": [],
        "genesis_org": "",
        "demo_link": "",
        "completeness_score": 0
    }
    
    # Extract title (project name) - look for pattern before (D####)
    title_match = re.search(r'2025(.+?)\(D\d+\)', content_md_text)
    if title_match:
        title = title_match.group(1).strip()
        # Clean up any asterisks or extra whitespace
        title = re.sub(r'\*+', '', title).strip()
        project["title"] = title
    
    # Extract team
    team_match = re.search(r'\*\*Team\s+([^\*]+)', content_md_text)
    if team_match:
        project["team"] = team_match.group(1).strip()
    
    # Extract main problem description (first paragraph after title)
    problem_match = re.search(r'View Voters\s*\n(.+?)(?:Attachments|Organization)', content_md_text, re.DOTALL)
    if problem_match:
        problem_text = problem_match.group(1).strip()
        # Clean up extra whitespace and line breaks
        problem_text = re.sub(r'\s+', ' ', problem_text)
        project["problem"] = problem_text
    
    # Extract solution overview
    solution_match = re.search(r'Solution Overview\*\s*\n(.+?)(?:Value Proposition|Additional Information)', content_md_text, re.DOTALL)
    if solution_match:
        solution_text = solution_match.group(1).strip()
        project["solution"] = solution_text
    
    # Extract value proposition
    value_match = re.search(r'Value Proposition\*\s*\n(.+?)(?:Additional Information|Completed PowerPoint)', content_md_text, re.DOTALL)
    if value_match:
        value_text = value_match.group(1).strip()
        project["value"] = value_text
    
    # Extract additional technical information
    tech_match = re.search(r'Additional Information\s*\n(.+?)(?:Completed PowerPoint|Link to Recorded Demo)', content_md_text, re.DOTALL)
    if tech_match:
        tech_text = tech_match.group(1).strip()
        if tech_text and tech_text != "No answer":
            project["technical_details"] = tech_text
    
    # Extract Genesis organization
    org_match = re.search(r'Genesis Organization for your Agent\(s\):\*\s*([^\n]+?)(?:Please|$)', content_md_text)
    if org_match:
        org = org_match.group(1).strip()
        # Remove any trailing "Please provide" text
        org = re.sub(r'Please.*$', '', org).strip()
        project["genesis_org"] = org
    
    # Extract agent names
    agent_match = re.search(r'Agent Name\(s\) as listed in Genesis:\*\s*\n(.+?)(?:Please certify|We used|$)', content_md_text, re.DOTALL)
    if agent_match:
        agent_text = agent_match.group(1).strip()
        # Split by newlines and clean up
        agents = [a.strip() for a in agent_text.split('\n') if a.strip() and not a.strip().startswith('http') and not a.strip().startswith('﻿')]
        project["agents"] = agents
    
    # Extract demo link
    demo_match = re.search(r'Link to Recorded Demo\*\s*([^\n]+?)(?:Please|$)', content_md_text)
    if demo_match:
        link = demo_match.group(1).strip()
        # Clean up the link
        link = re.sub(r'Please.*$', '', link).strip()
        project["demo_link"] = link
    
    # Calculate completeness score (0-100)
    score = 0
    if project["title"]: score += 15
    if project["team"]: score += 10
    if project["problem"]: score += 20
    if project["solution"]: score += 20
    if project["value"]: score += 15
    if project["technical_details"]: score += 10
    if project["agents"]: score += 5
    if project["genesis_org"]: score += 5
    
    project["completeness_score"] = score
    
    return project


def generate_specification(project, page_folder):
    """Generate a specification document for the project"""
    
    spec_content = f"""# Project Specification: {project['title']}

**Project ID:** {project['id']}  
**Team:** {project['team']}  
**Genesis Organization:** {project['genesis_org']}  

---

## 1. Problem Statement

{project['problem'] if project['problem'] else '*No problem statement provided*'}

---

## 2. Solution Overview

{project['solution'] if project['solution'] else '*No solution overview provided*'}

---

## 3. Value Proposition

{project['value'] if project['value'] else '*No value proposition provided*'}

---

## 4. Technical Architecture

### AI Agents
{chr(10).join(f"- {agent}" for agent in project['agents']) if project['agents'] else '*No agent information provided*'}

### Technical Details
{project['technical_details'] if project['technical_details'] else '*No technical details provided*'}

---

## 5. Deliverables

- **Demo Recording:** {project['demo_link'] if project['demo_link'] else '*Not provided*'}
- **PowerPoint:** See attachments folder
- **Genesis Organization:** {project['genesis_org'] if project['genesis_org'] else '*Not provided*'}

---

## 6. Implementation Status

*Status information to be added*

---

## Specification Completeness: {project['completeness_score']}%

"""
    
    # Write specification file
    spec_file = page_folder / "PROJECT_SPEC.md"
    with open(spec_file, "w", encoding="utf-8") as f:
        f.write(spec_content)
    
    return spec_file


def main():
    """Process all project folders and generate specifications"""
    
    # Find all project directories
    page_folders = sorted([d for d in BASE_DIR.iterdir() if d.is_dir() and d.name.startswith("D")])
    
    logging.info(f"Found {len(page_folders)} project folders")
    
    incomplete_projects = []
    completed_specs = []
    
    for page_folder in page_folders:
        page_id = page_folder.name
        content_md = page_folder / "content.md"
        
        if not content_md.exists():
            logging.warning(f"  {page_id}: No content.md file found - skipping")
            incomplete_projects.append({
                "id": page_id,
                "reason": "Missing content.md file"
            })
            continue
        
        logging.info(f"Processing {page_id}...")
        
        # Read content
        with open(content_md, "r", encoding="utf-8") as f:
            content_text = f.read()
        
        # Extract project information
        project = extract_project_info(content_text, page_id)
        
        # Generate specification
        spec_file = generate_specification(project, page_folder)
        logging.info(f"  ✓ Generated: {spec_file}")
        logging.info(f"  Completeness: {project['completeness_score']}%")
        
        completed_specs.append({
            "id": page_id,
            "title": project["title"],
            "score": project["completeness_score"]
        })
        
        # Track incomplete projects (< 70% complete)
        if project["completeness_score"] < 70:
            incomplete_projects.append({
                "id": page_id,
                "title": project["title"],
                "score": project["completeness_score"],
                "missing": []
            })
            
            # Identify what's missing
            if not project["problem"]:
                incomplete_projects[-1]["missing"].append("Problem statement")
            if not project["solution"]:
                incomplete_projects[-1]["missing"].append("Solution overview")
            if not project["value"]:
                incomplete_projects[-1]["missing"].append("Value proposition")
            if not project["technical_details"]:
                incomplete_projects[-1]["missing"].append("Technical details")
    
    # Generate incomplete projects list
    if incomplete_projects:
        logging.info(f"\nGenerating incomplete projects list...")
        
        with open(INCOMPLETE_LIST_FILE, "w", encoding="utf-8") as f:
            f.write("# Projects Needing More Detail\n\n")
            f.write(f"**Generated:** {logging.Formatter().formatTime(logging.makeLogRecord({}))}\n\n")
            f.write(f"**Total projects needing detail:** {len(incomplete_projects)}\n\n")
            f.write("---\n\n")
            
            for proj in incomplete_projects:
                f.write(f"## {proj['id']}: {proj.get('title', 'Unknown')}\n\n")
                f.write(f"**Completeness Score:** {proj.get('score', 0)}%\n\n")
                
                if proj.get("missing"):
                    f.write("**Missing Information:**\n")
                    for item in proj["missing"]:
                        f.write(f"- {item}\n")
                else:
                    f.write(f"**Reason:** {proj.get('reason', 'Unknown')}\n")
                
                f.write("\n")
        
        logging.info(f"  ✓ Created: {INCOMPLETE_LIST_FILE}")
    else:
        logging.info("\n✓ All projects have sufficient detail!")
    
    # Summary
    logging.info("\n" + "="*70)
    logging.info("Summary:")
    logging.info(f"  Total projects: {len(page_folders)}")
    logging.info(f"  Specifications generated: {len(completed_specs)}")
    logging.info(f"  Projects needing detail: {len(incomplete_projects)}")
    logging.info("="*70)


if __name__ == "__main__":
    main()
