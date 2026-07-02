# Professional Development Self-Assessment Application (Detailed Version)

A Python application that guides you through a comprehensive self-assessment with **detailed subcategory questions** and visualizes your aggregated results as an interactive radar chart.

## What's New in Version 2

- **Detailed sub-questions**: 3-5 specific questions per category
- **~70 total questions** for comprehensive assessment
- **Averaged scores**: Sub-questions are averaged per category for the radar chart
- **Detailed breakdown view**: See individual question scores organized by category
- **Better insights**: More granular data to identify specific strengths and weaknesses

## Features

- **Comprehensive questionnaire** with 18 main categories
- **3-5 detailed sub-questions** per category (70+ total questions)
- **Category-level radar chart** showing averaged scores
- **Detailed results view** with all individual question scores
- **Date-stamped results** for tracking progress over time
- **PNG export** to save and compare assessments
- **User-friendly interface** with progress tracking

## Assessment Categories & Sub-Questions

### 1. Technical Skills (4 questions)
   - Proficiency with core tools and technologies
   - Ability to learn new technical tools
   - Quality of technical work output
   - Technical troubleshooting skills

### 2. Interpersonal Skills (4 questions)
   - Building positive relationships
   - Reading social cues
   - Showing empathy and emotional awareness
   - Navigating workplace dynamics

### 3. Communication (4 questions)
   - Written communication clarity
   - Verbal communication and presentations
   - Active listening
   - Adapting communication to audiences

### 4. Learning Ability (4 questions)
   - Speed of understanding new concepts
   - Retention and application
   - Self-directed learning
   - Learning from feedback

### 5. Leadership (4 questions)
   - Inspiring and motivating others
   - Decision-making with confidence
   - Delegating effectively
   - Developing and mentoring

### 6. Problem Solving (4 questions)
   - Breaking down complex problems
   - Identifying root causes
   - Generating creative solutions
   - Evaluating tradeoffs

### 7. Learning Habits & Development (4 questions)
   - Consistency in professional development
   - Staying current with industry trends
   - Applying new knowledge
   - Seeking learning opportunities

### 8. Emotional Intelligence (4 questions)
   - Self-awareness of emotions
   - Understanding others' emotions
   - Managing emotions in stress
   - Building trust and rapport

### 9. Systems Thinking (4 questions)
   - Understanding system interactions
   - Seeing patterns and connections
   - Considering downstream effects
   - Strategic long-term thinking

### 10. Adaptability (4 questions)
   - Adjusting to unexpected changes
   - Staying effective in ambiguity
   - Pivoting strategies
   - Responding to feedback constructively

### 11. Time Management (4 questions)
   - Meeting deadlines consistently
   - Estimating task duration
   - Prioritizing effectively
   - Minimizing procrastination

### 12. Creativity (4 questions)
   - Generating novel ideas
   - Challenging conventional thinking
   - Thinking laterally
   - Balancing creativity with constraints

### 13. Collaboration (4 questions)
   - Contributing in team settings
   - Compromising and finding middle ground
   - Giving and receiving help
   - Handling team conflicts

### 14. Attention to Detail (4 questions)
   - Catching errors
   - Balancing perfectionism with pragmatism
   - Following through on details
   - Maintaining quality standards

### 15. Self-Motivation (4 questions)
   - Maintaining drive without supervision
   - Taking initiative
   - Following through on commitments
   - Sustaining energy over time

### 16. Decision Making (4 questions)
   - Making timely decisions
   - Weighing risks and benefits
   - Standing behind decisions
   - Track record of outcomes

### 17. Cultural Awareness (4 questions)
   - Understanding diverse perspectives
   - Using inclusive behavior
   - Being open to unfamiliar ideas
   - Recognizing unconscious biases

### 18. Influence & Persuasion (4 questions)
   - Convincing others without authority
   - Negotiating effectively
   - Building consensus
   - Presenting ideas compellingly

> **Note:** Financial Skills (business/budget management) is available but currently commented out. Uncomment in code if relevant.

## Installation

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the detailed version:**
   ```bash
   python self_assessment_app_v2.py
   ```

## Usage

1. **Answer detailed questions**: Rate yourself on a scale of 1-5 for each specific sub-question
   - 1 = Needs Significant Improvement
   - 5 = Exceptional
   - ~70 questions total (takes 10-15 minutes)

2. **Track your progress**: The UI shows which category and sub-question you're on

3. **View aggregated results**: After completing all questions, click "View Results" to see your radar chart with **category averages**

4. **View detailed breakdown**: Click "View Details" to see all individual question scores organized by category

5. **Save chart**: Click "Save as PNG" to export your radar chart with timestamp

6. **Start over**: Click "Start Over" to begin a new assessment

## How Scoring Works

- Each sub-question is rated 1-5
- **Category scores** are calculated as the **average** of all sub-questions in that category
- The radar chart displays these averaged category scores
- Individual question scores are available in the detailed breakdown view

**Example:**
```
Technical Skills:
  - Tool proficiency: 4/5
  - Learning new tools: 4/5
  - Work quality: 3/5
  - Troubleshooting: 4/5
  → Category Average: 3.8/5 (shown on radar chart)
```

## Chart Details

The radar chart includes:
- Category averages plotted on a polar coordinate system
- All 18 category labels clearly visible
- Date and time of assessment
- Overall average score across all categories
- Note indicating number of detailed questions answered
- High-resolution output (300 DPI) for printing

## Benefits of Detailed Assessment

✓ **More accurate**: Multiple questions per category reduce bias
✓ **Better insights**: Identify specific sub-skills to improve
✓ **Actionable**: Know exactly which aspects of each category need work
✓ **Comprehensive**: ~70 questions provide thorough evaluation
✓ **Still visual**: Category averages keep the radar chart clean and readable

## Tips for Tracking Professional Growth

- Take the full detailed assessment quarterly or bi-annually
- Compare category averages over time to track broad progress
- Use the detailed breakdown to create targeted development plans
- Focus on specific sub-questions that scored lowest
- Reassess after working on development areas to measure improvement
- Share detailed results with mentors during career discussions

## Example Workflow

```
1. Complete detailed assessment (70 questions) → ~15 minutes
2. Review radar chart to identify weak categories
3. Check detailed breakdown for specific sub-skills needing work
4. Create development plan targeting lowest-scoring sub-questions
5. Work on improvements for 3-6 months
6. Retake assessment → Compare results
7. Share progress with manager/mentor
```

## Comparison: Simple vs. Detailed Version

| Feature | Simple (v1) | Detailed (v2) |
|---------|-------------|---------------|
| Questions | 18 | ~70 |
| Time | 3-5 min | 10-15 min |
| Granularity | Category-level | Sub-question level |
| Insights | General strengths/weaknesses | Specific skills to improve |
| Best for | Quick check-ins | Comprehensive review |

## Requirements

- Python 3.7+
- matplotlib
- numpy
- tkinter (usually included with Python)
