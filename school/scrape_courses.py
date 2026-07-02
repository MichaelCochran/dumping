import requests
from bs4 import BeautifulSoup
import re
import urllib3

# Suppress SSL warnings for corporate proxy
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def parse_course_line(line):
    """Parse a course line to extract course code and number"""
    line = line.strip()
    
    # Handle special case for CS/ECE/PUBP 6727
    if line.startswith('CS/ECE/PUBP'):
        return [('CS', '6727'), ('ECE', '6727'), ('PUBP', '6727')]
    
    # Extract course prefix and number
    match = re.match(r'^([A-Z]+)\s+(\d+)', line)
    if match:
        return [(match.group(1), match.group(2))]
    return []

def get_course_description(dept, course_num):
    """Fetch course description from Georgia Tech catalog"""
    dept_lower = dept.lower()
    url = f"https://catalog.gatech.edu/coursesaz/{dept_lower}/"
    
    try:
        response = requests.get(url, timeout=10, verify=False)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find all course blocks
        course_blocks = soup.find_all('div', class_='courseblock')
        
        for block in course_blocks:
            # Get course title which contains the course code
            title_elem = block.find('p', class_='courseblocktitle')
            if not title_elem:
                continue
                
            title_text = title_elem.get_text().strip()
            
            # Normalize whitespace
            title_text = ' '.join(title_text.split())
            
            # Check if this is the course we're looking for
            # Look for pattern like "CS 6035." or "CS 6035 " at the start
            search_pattern = f'{dept} {course_num}.'
            if title_text.startswith(search_pattern) or f'{dept} {course_num} ' in title_text[:20]:
                # Extract course name
                # Format is usually: "CS 6035. Introduction to Information Security. 3 Credit Hours."
                parts = title_text.split('.')
                if len(parts) >= 2:
                    course_name = parts[1].strip()
                    # Remove credit hours if present
                    if len(parts) > 2 and 'Credit' in parts[2]:
                        pass  # course_name is already correct
                else:
                    course_name = title_text.strip()
                
                # Get description
                desc_elem = block.find('p', class_='courseblockdesc')
                if desc_elem:
                    description = desc_elem.get_text().strip()
                    # Clean up whitespace
                    description = ' '.join(description.split())
                else:
                    description = "No description available"
                
                return course_name, description
        
        return None, "Course not found in catalog"
    
    except Exception as e:
        return None, f"Error fetching course: {str(e)}"

def main():
    # Read input file
    with open('ga_tech.txt', 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Parse courses
    courses = []
    seen = set()
    
    for line in lines:
        parsed = parse_course_line(line)
        for dept, num in parsed:
            key = f"{dept} {num}"
            if key not in seen:
                seen.add(key)
                courses.append((dept, num, line.strip()))
    
    # Fetch descriptions and write output
    with open('courses.txt', 'w', encoding='utf-8') as f:
        for i, (dept, num, original_line) in enumerate(courses, 1):
            print(f"Fetching {i}/{len(courses)}: {dept} {num}")
            
            course_name, description = get_course_description(dept, num)
            
            if course_name:
                f.write(f"{dept} {num}: {course_name}\n")
                f.write(f"{description}\n")
                f.write("-" * 80 + "\n\n")
            else:
                # If not found, try to use the name from the original file
                match = re.match(r'^([A-Z/]+)\s+(\d+):\s*(.+)$', original_line)
                if match:
                    name_from_file = match.group(3).strip()
                    f.write(f"{dept} {num}: {name_from_file}\n")
                    f.write(f"{description}\n")
                    f.write("-" * 80 + "\n\n")
                else:
                    f.write(f"{dept} {num}: Unknown\n")
                    f.write(f"{description}\n")
                    f.write("-" * 80 + "\n\n")
    
    print(f"\nComplete! Course descriptions saved to courses.txt")

if __name__ == "__main__":
    main()
