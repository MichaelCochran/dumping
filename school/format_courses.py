import re
import csv

def parse_courses_file(filename):
    """Parse the existing courses.txt file"""
    courses = []
    
    with open(filename, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        
        # Check if this is a course title line
        match = re.match(r'^([A-Z]+)\s+(\d+):\s*(.+)$', line)
        if match:
            dept = match.group(1)
            number = match.group(2)
            name = match.group(3)
            
            # Get description from next line
            i += 1
            if i < len(lines):
                description = lines[i].strip()
            else:
                description = ""
            
            courses.append({
                'dept': dept,
                'number': number,
                'code': f"{dept} {number}",
                'name': name,
                'description': description
            })
        
        i += 1
    
    return courses

def write_markdown(courses, filename):
    """Write courses in a clean markdown format"""
    with open(filename, 'w', encoding='utf-8') as f:
        f.write("# Georgia Tech Course Catalog\n\n")
        
        # Group by department
        depts = {}
        for course in courses:
            dept = course['dept']
            if dept not in depts:
                depts[dept] = []
            depts[dept].append(course)
        
        # Write each department section
        for dept in sorted(depts.keys()):
            dept_name = {
                'CS': 'Computer Science',
                'ECE': 'Electrical & Computer Engineering',
                'PUBP': 'Public Policy',
                'INTA': 'International Affairs',
                'MGT': 'Management'
            }.get(dept, dept)
            
            f.write(f"## {dept_name} ({dept})\n\n")
            
            for course in sorted(depts[dept], key=lambda x: x['number']):
                f.write(f"### {course['code']}: {course['name']}\n\n")
                if course['description']:
                    f.write(f"{course['description']}\n\n")
                else:
                    f.write("*No description available*\n\n")
                f.write("---\n\n")

def write_csv(courses, filename):
    """Write courses in CSV format"""
    with open(filename, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['dept', 'number', 'code', 'name', 'description'])
        writer.writeheader()
        
        # Sort by department and number
        sorted_courses = sorted(courses, key=lambda x: (x['dept'], int(x['number'])))
        writer.writerows(sorted_courses)

def write_table(courses, filename):
    """Write courses in a simple table format"""
    with open(filename, 'w', encoding='utf-8') as f:
        f.write("=" * 120 + "\n")
        f.write(f"{'CODE':<12} | {'COURSE NAME':<60} | {'DEPT':<8}\n")
        f.write("=" * 120 + "\n\n")
        
        # Group by department
        depts = {}
        for course in courses:
            dept = course['dept']
            if dept not in depts:
                depts[dept] = []
            depts[dept].append(course)
        
        for dept in sorted(depts.keys()):
            dept_name = {
                'CS': 'Computer Science',
                'ECE': 'Electrical & Computer Engineering',
                'PUBP': 'Public Policy',
                'INTA': 'International Affairs',
                'MGT': 'Management'
            }.get(dept, dept)
            
            f.write(f"\n{'─' * 120}\n")
            f.write(f"{dept_name} ({dept})\n")
            f.write(f"{'─' * 120}\n\n")
            
            for course in sorted(depts[dept], key=lambda x: int(x['number'])):
                f.write(f"{course['code']:<12} | {course['name']:<60}\n")
                
                # Wrap description at 116 characters
                if course['description']:
                    desc = course['description']
                    wrapper_width = 116
                    words = desc.split()
                    lines = []
                    current_line = ""
                    
                    for word in words:
                        if len(current_line) + len(word) + 1 <= wrapper_width:
                            if current_line:
                                current_line += " " + word
                            else:
                                current_line = word
                        else:
                            if current_line:
                                lines.append(current_line)
                            current_line = word
                    
                    if current_line:
                        lines.append(current_line)
                    
                    for line in lines:
                        f.write(f"             | {line}\n")
                else:
                    f.write(f"             | (No description available)\n")
                
                f.write("\n")
        
        f.write("=" * 120 + "\n")

def main():
    print("Parsing courses.txt...")
    courses = parse_courses_file('courses.txt')
    print(f"Found {len(courses)} courses\n")
    
    print("Creating formatted versions...")
    write_markdown(courses, 'courses_formatted.md')
    print("✓ Created courses_formatted.md (Markdown format)")
    
    write_csv(courses, 'courses.csv')
    print("✓ Created courses.csv (CSV format for easy parsing)")
    
    write_table(courses, 'courses_table.txt')
    print("✓ Created courses_table.txt (Clean table format)")
    
    print("\nDone! You can now view:")
    print("  - courses_formatted.md  (best for reading)")
    print("  - courses_table.txt     (compact overview)")
    print("  - courses.csv           (for spreadsheet/programming)")

if __name__ == "__main__":
    main()
