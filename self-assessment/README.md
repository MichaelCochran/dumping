# Professional Development Self-Assessment Application

A Python application that guides you through a comprehensive self-assessment and visualizes your results as 
an interactive radar chart. This tool is designed to help you evaluate your workplace skills and career capabilities.

## Features

- **Interactive questionnaire** with 18 assessment categories
- **Visual radar chart** displaying your strengths and weaknesses
- **Date-stamped results** for tracking progress over time
- **PNG export** to save and compare assessments
- **User-friendly interface** with progress tracking

## Assessment Categories

The app evaluates you across 18 key professional dimensions:

1. Technical Skills
2. Interpersonal Skills
3. Communication
4. Learning Ability
5. Leadership
6. Problem Solving
7. Learning Habits & Development
8. Emotional Intelligence
9. Systems Thinking
10. Adaptability
11. Time Management
12. Creativity
13. Collaboration
14. Attention to Detail
15. Self-Motivation
16. Decision Making
17. Cultural Awareness
18. Influence & Persuasion

> **Note:** Financial Skills (business/budget management) is currently commented out but can be enabled in the code if relevant to your context.

## Installation

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the application:**
   ```bash
   python self_assessment_app.py
   ```

## Usage

1. **Answer questions**: Rate yourself on a scale of 1-10 for each category
   - 1 = Needs Significant Improvement
   - 10 = Exceptional

2. **Navigate**: Use "Next" and "Previous" buttons to move through questions

3. **View results**: After completing all questions, click "View Results" to see your radar chart

4. **Save chart**: Click "Save as PNG" to export your chart with timestamp

5. **Start over**: Click "Start Over" to begin a new assessment

## Chart Details

The radar chart includes:
- Your scores plotted on a polar coordinate system
- All 18 category labels clearly visible
- Date and time of assessment
- Average score calculation
- High-resolution output (300 DPI) for printing

## Tips for Tracking Professional Growth

- Save your charts with descriptive filenames (e.g., `professional_dev_2026_Q1.png`)
- Take assessments at regular intervals (quarterly, after performance reviews, annually)
- Compare charts side-by-side to identify skill development areas
- Use the date stamp to track your career development journey
- Consider taking assessments before/after major projects, promotions, or role changes

## Example Workflow

```
1. Complete initial assessment → Save as "career_baseline_2026.png"
2. Work on identified development areas for 3-6 months
3. Complete follow-up assessment → Save as "progress_2026_Q3.png"
4. Compare charts to see improvements
5. Share results with mentor or during performance review discussions
```

## Requirements

- Python 3.7+
- matplotlib
- numpy
- tkinter (usually included with Python)
