#!/usr/bin/env python3
import argparse
import random
import os
from pathlib import Path

def parse_questions(file_path, target_sections):
    """Parse the markdown file and extract questions from target sections."""
    questions = []
    current_section = None
    in_target_section = False
    
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            
            # Check if this is a section header
            if line.startswith('## '):
                section_name = line[3:].strip()
                in_target_section = section_name in target_sections
                current_section = section_name
            
            # Collect questions from target sections
            elif in_target_section and line.startswith('- '):
                question_text = line[2:].strip()
                questions.append({
                    'section': current_section,
                    'question': question_text
                })
    
    return questions

def main():
    parser = argparse.ArgumentParser(description='Randomly select check-in questions')
    parser.add_argument('-k', '--kids', action='store_true', 
                        help='Select questions from Kids section (default: work sections)')
    parser.add_argument('-c', '--count', type=int, 
                        help='Number of questions to select (default: 10 for work, 5 for kids)')
    
    args = parser.parse_args()
    
    # Determine file path
    script_dir = Path(__file__).parent
    file_path = script_dir / "check-ins.md"
    
    if not file_path.exists():
        print(f"Error: Could not find {file_path}")
        return 1
    
    # Determine count and sections
    if args.kids:
        target_count = args.count if args.count else 5
        target_sections = ["Check-in Questions for Kids"]
    else:
        target_count = args.count if args.count else 10
        target_sections = [
            "Daily Check-in Questions",
            "Emotional Check-in Questions for Adults",
            "Fun Check-in Questions",
            "Mindset Check-in Questions",
            "Check-in Questions for Employees",
            "Check-in Questions for Teams"
        ]
    
    # Parse and collect questions
    questions = parse_questions(file_path, target_sections)
    
    if not questions:
        print("No questions found in the specified sections.")
        return 1
    
    # Randomly select questions
    selected_count = min(target_count, len(questions))
    selected_questions = random.sample(questions, selected_count)
    
    # Display results
    print("\n=== Check-in Questions ===\n")
    
    for i, q in enumerate(selected_questions, 1):
        print(f"{i}. {q['question']}")
        print(f"   ({q['section']})\n")
    
    return 0

if __name__ == "__main__":
    exit(main())
