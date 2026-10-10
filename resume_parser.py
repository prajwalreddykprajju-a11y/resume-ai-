import os
import re
import json

# Try importing fitz (PyMuPDF) and docx
try:
    import fitz
except ImportError:
    fitz = None

try:
    import docx
except ImportError:
    docx = None

# Comprehensive Skills Dictionary for CS, AI, Data Science, Web & Software Engineering
SKILL_DICTIONARY = {
    'Programming Languages': [
        'python', 'java', 'c++', 'c', 'c#', 'javascript', 'typescript', 'html', 'css', 
        'sql', 'r', 'go', 'rust', 'kotlin', 'swift', 'php', 'ruby'
    ],
    'Databases & Storage': [
        'sqlite', 'mysql', 'postgresql', 'mongodb', 'redis', 'oracle', 'dynamodb', 
        'firebase', 'cassandra', 'sql server'
    ],
    'AI, ML & Data Science': [
        'machine learning', 'deep learning', 'artificial intelligence', 'nlp', 'natural language processing',
        'computer vision', 'opencv', 'tensorflow', 'pytorch', 'scikit-learn', 'pandas', 'numpy', 
        'matplotlib', 'seaborn', 'keras', 'data analysis', 'data visualization', 'transformers',
        'huggingface', 'spacy', 'nltk', 'llm', 'generative ai'
    ],
    'Web & Frameworks': [
        'flask', 'django', 'fastapi', 'express', 'node.js', 'react', 'vue.js', 'angular', 
        'bootstrap', 'tailwind', 'rest api', 'graphql', 'jinja', 'jquery', 'next.js'
    ],
    'Tools, DevOps & Cloud': [
        'git', 'github', 'gitlab', 'docker', 'kubernetes', 'aws', 'azure', 'gcp', 
        'linux', 'bash', 'postman', 'jira', 'ci/cd', 'vscode', 'jupyter', 'conda'
    ],
    'Professional & Soft Skills': [
        'communication', 'problem solving', 'teamwork', 'leadership', 'time management', 
        'agile', 'scrum', 'critical thinking', 'analytical skills', 'project management'
    ]
}

def extract_text_from_pdf(filepath):
    """Extract text from PDF using PyMuPDF (fitz)."""
    text = ""
    if not fitz:
        raise ImportError("PyMuPDF (fitz) is not installed.")
    
    doc = fitz.open(filepath)
    for page in doc:
        text += page.get_text() + "\n"
    doc.close()
    return text

def extract_text_from_docx(filepath):
    """Extract text from DOCX file using python-docx."""
    if not docx:
        raise ImportError("python-docx is not installed.")
    
    doc = docx.Document(filepath)
    full_text = []
    for para in doc.paragraphs:
        full_text.append(para.text)
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                full_text.append(cell.text)
    return "\n".join(full_text)

def extract_text(filepath, file_type):
    """General document text extractor with graceful error handling."""
    ext = file_type.lower()
    text = ""
    if ext == 'pdf' or filepath.endswith('.pdf'):
        try:
            text = extract_text_from_pdf(filepath)
        except Exception as e:
            text = ""
    elif ext in ['docx', 'doc'] or filepath.endswith('.docx'):
        try:
            text = extract_text_from_docx(filepath)
        except Exception as e:
            text = ""
    elif filepath.endswith('.txt'):
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            text = f.read()

    return text.strip()

def parse_email(text):
    match = re.search(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', text)
    return match.group(0) if match else "Not found"


def parse_phone(text):
    """Extract Indian mobile numbers with optional +91 country code."""
    pattern = r'(?<!\d)(?:\+?91[\s().-]*)?([6-9]\d{4}[\s().-]*\d{5})(?!\d)|(?<!\d)(?:\+?91[\s().-]*)?([6-9]\d{9})(?!\d)'
    match = re.search(pattern, text)

    if match:
        mobile = match.group(1) or match.group(2)
        digits = re.sub(r'\D', '', mobile)
        if len(digits) == 10 and digits[0] in "6789":
            return mobile

    return "Not found"


def parse_links(text):
    links = []
    github = re.search(r'(https?://)?(www\.)?github\.com/[a-zA-Z0-9_-]+', text, re.I)
    linkedin = re.search(r'(https?://)?(www\.)?linkedin\.com/in/[a-zA-Z0-9_-]+', text, re.I)
    portfolio = re.findall(r'https?://[^\s]+', text)
    
    if github: links.append(github.group(0))
    if linkedin: links.append(linkedin.group(0))
    for p in portfolio:
        if p not in links and 'github' not in p and 'linkedin' not in p:
            links.append(p)
    return links if links else ["Not found"]

def parse_name(text):
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    if not lines:
        return "Not found"
    
    # Usually the candidate name is in the first 3 lines
    for line in lines[:3]:
        # Filter out email, phone, addresses
        if '@' in line or re.search(r'\d', line) or 'resume' in line.lower() or 'curriculum' in line.lower():
            continue
        words = line.split()
        if 1 <= len(words) <= 4 and all(w.isalpha() or '.' in w for w in words):
            return line.title()
    return lines[0].title() if lines else "Not found"

def parse_education(text):
    degree_patterns = [
        r'(B\.?Tech|Bachelor of Technology)',
        r'(B\.?E\.?|Bachelor of Engineering)',
        r'(B\.?Sc|Bachelor of Science)',
        r'(BCA|Bachelor of Computer Applications)',
        r'(M\.?Tech|Master of Technology)',
        r'(M\.?Sc|Master of Science)',
        r'(MCA|Master of Computer Applications)',
        r'(B\.?Com|Bachelor of Commerce)',
        r'(MBA|Master of Business Administration)'
    ]
    
    degree = "Not found"
    university = "Not found"
    grad_year = "Not found"

    for pattern in degree_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            degree = match.group(0)
            break

    # Look for university keywords
    univ_match = re.search(r'([A-Z][A-Za-z\s,&]+(University|Institute|College|Academy|School))', text)
    if univ_match:
        univ = univ_match.group(0).strip()
        if len(univ) < 80:
            university = univ

    # Look for graduation year prioritizing explicit labels & end years
    grad_year = "Not found"

    # Priority 1: Explicitly labeled expected graduation / graduation year
    # e.g., "Expected Graduation: 2029", "Graduation Year: 2026", "Graduating 2028", "Class of 2027", "Batch 2026", "Expected: 2029"
    labeled_match = re.search(
        r'(?:Expected\s+Graduation|Graduation\s+Year|Graduation|Graduating|Class\s+of|Batch\s+of|Expected)[\s:\-]*([20][234][0-9])',
        text, re.IGNORECASE
    )
    if labeled_match:
        grad_year = labeled_match.group(1)
    else:
        # Priority 2: Year range e.g. "2025–2029", "2022 - 2026", "2025 to 2029" (capture second/end year)
        range_match = re.search(r'20[1234][0-9]\s*[\-–—to]+\s*(20[1234][0-9])', text, re.IGNORECASE)
        if range_match:
            grad_year = range_match.group(1)
        else:
            # Priority 3: Any 4-digit year NOT followed by "-Present" or "-Current"
            years = re.findall(r'20[1234][0-9]', text)
            for y in years:
                pattern = re.escape(y) + r'\s*[\-–—]\s*(?:Present|Current)'
                if not re.search(pattern, text, re.IGNORECASE):
                    grad_year = y
                    break
            
            # Fallback if only start year was found
            if grad_year == "Not found" and years:
                grad_year = years[0]

    return {
        'degree': degree,
        'university': university,
        'grad_year': grad_year
    }

def parse_yearwise_cgpa(text):
    """
    Extract Year 1, Year 2, Year 3, Year 4 CGPAs and overall CGPA.
    Returns dictionary with CGPA values and statuses.
    """
    cgpa_data = {
        'cgpa_y1': 'Pending',
        'cgpa_y2': 'Pending',
        'cgpa_y3': 'Pending',
        'cgpa_y4': 'Pending',
        'overall_cgpa': 'Not calculated',
        'cgpa_status_y1': 'Pending',
        'cgpa_status_y2': 'Pending',
        'cgpa_status_y3': 'Pending',
        'cgpa_status_y4': 'Pending',
        'overall_cgpa_type': 'user_provided',
        'scale': 10.0
    }

    # Regex patterns for year-wise CGPA
    # e.g., "Year 1 CGPA: 8.2", "1st Year: 7.7", "Y1 CGPA: 8.5", "Sem 1 & 2 CGPA: 8.1"
    patterns = [
        (r'(?:Year 1|1st Year|Y1|Sem 1|Semester 1)(?:\s*(?:CGPA|SGPA|GPA))?[\s:\-]*([0-9]\.[0-9]{1,2})', 'cgpa_y1'),
        (r'(?:Year 2|2nd Year|Y2|Sem 3|Semester 3)(?:\s*(?:CGPA|SGPA|GPA))?[\s:\-]*([0-9]\.[0-9]{1,2})', 'cgpa_y2'),
        (r'(?:Year 3|3rd Year|Y3|Sem 5|Semester 5)(?:\s*(?:CGPA|SGPA|GPA))?[\s:\-]*([0-9]\.[0-9]{1,2})', 'cgpa_y3'),
        (r'(?:Year 4|4th Year|Y4|Sem 7|Semester 7)(?:\s*(?:CGPA|SGPA|GPA))?[\s:\-]*([0-9]\.[0-9]{1,2})', 'cgpa_y4'),
    ]

    for pattern, key in patterns:
        m = re.search(pattern, text, re.IGNORECASE)
        if m:
            val = m.group(1)
            try:
                if 0.0 <= float(val) <= 10.0:
                    cgpa_data[key] = val
                    cgpa_data['cgpa_status_' + key.split('_')[1]] = 'Completed'
            except ValueError:
                pass

    # Overall CGPA search (prioritize explicit Overall / Aggregate keywords)
    overall_match = re.search(r'(?:Overall\s+CGPA|Aggregate\s+CGPA|Overall\s+CPI|Overall\s+GPA|Overall)[\s:\-]*([0-9]\.[0-9]{1,2})', text, re.IGNORECASE)
    if not overall_match:
        overall_match = re.search(r'(?:CGPA|CPI|GPA)[\s:\-]*([0-9]\.[0-9]{1,2})', text, re.IGNORECASE)
        
    if overall_match:
        val = overall_match.group(1)
        try:
            if 0.0 <= float(val) <= 10.0:
                cgpa_data['overall_cgpa'] = val
        except ValueError:
            pass

    return cgpa_data

def parse_skills(text):
    text_lower = text.lower()
    found_skills = []
    
    for category, skills_list in SKILL_DICTIONARY.items():
        for skill in skills_list:
            # Word boundary regex for accurate matching (e.g. C vs C++)
            pattern = r'\b' + re.escape(skill) + r'\b'
            if skill in ['c++', 'c#', '.net', 'node.js', 'vue.js', 'next.js']:
                pattern = re.escape(skill)
            
            if re.search(pattern, text_lower):
                # Capitalize display nicely
                display_name = skill.upper() if len(skill) <= 4 and skill not in ['java', 'rust', 'html', 'css', 'bash'] else skill.title()
                if skill == 'c++': display_name = 'C++'
                if skill == 'c#': display_name = 'C#'
                if skill == 'nlp': display_name = 'NLP'
                if skill == 'llm': display_name = 'LLM'
                if skill == 'ai': display_name = 'AI'
                if skill == 'sql': display_name = 'SQL'
                if skill == 'aws': display_name = 'AWS'
                if skill == 'gcp': display_name = 'GCP'

                if display_name not in found_skills:
                    found_skills.append(display_name)

    return sorted(list(set(found_skills)))

def parse_projects(text):
    """
    Extract project titles and descriptions cleanly.
    Ensures sentences are not truncated and unrelated sections (Experience, Skills, Certifications)
    do not bleed into the projects list.
    """
    projects = []
    lines = text.split('\n')
    in_project_section = False
    current_project_lines = []
    last_line_was_bullet = False

    section_end_pattern = r'^\s*(?:education|experience|work\s+experience|employment|internships?|work\s+history|certifications?|courses?|skills|technical\s+skills|key\s+skills|achievements?|awards?|honors?|extracurricular|activities|publications?|languages?|interests?|hobbies|declaration|references?|profile|summary|objective)\b'

    for line in lines:
        clean = line.strip()
        if not clean:
            continue

        if re.search(r'^\s*(?:projects|key\s+projects|academic\s+projects|capstone\s+projects|major\s+projects|personal\s+projects)\b', clean, re.IGNORECASE):
            in_project_section = True
            current_project_lines = []
            last_line_was_bullet = False
            continue

        if in_project_section:
            if re.search(section_end_pattern, clean, re.IGNORECASE):
                in_project_section = False
                break

            is_numbered = bool(re.match(r'^(?:\d+[\.\)]|Project\s+\d+:?)\s*', clean, re.IGNORECASE))
            is_bullet = bool(re.match(r'^(?:•|\-|\*)\s*', clean))

            if is_numbered:
                if current_project_lines:
                    full_proj = " ".join(current_project_lines).strip()
                    if full_proj:
                        projects.append(full_proj)
                    current_project_lines = []
                clean_text = re.sub(r'^(?:\d+[\.\)]|Project\s+\d+:?)\s*', '', clean).strip()
                if clean_text:
                    current_project_lines.append(clean_text)
                last_line_was_bullet = False

            elif is_bullet:
                clean_text = re.sub(r'^(?:•|\-|\*)\s*', '', clean).strip()
                if re.match(r'^[A-Z][A-Za-z0-9\s\.\-]{2,35}\s*:\s*', clean_text):
                    if current_project_lines:
                        full_proj = " ".join(current_project_lines).strip()
                        if full_proj:
                            projects.append(full_proj)
                        current_project_lines = []
                
                if clean_text:
                    current_project_lines.append(clean_text)
                last_line_was_bullet = True

            else:
                if last_line_was_bullet and current_project_lines:
                    full_proj = " ".join(current_project_lines).strip()
                    if full_proj:
                        projects.append(full_proj)
                    current_project_lines = [clean]
                    last_line_was_bullet = False
                else:
                    current_project_lines.append(clean)

    if current_project_lines:
        full_proj = " ".join(current_project_lines).strip()
        if full_proj:
            projects.append(full_proj)

    final_projects = []
    for p in projects:
        p_clean = re.sub(r'\s+', ' ', p).strip()
        if len(p_clean) > 5 and p_clean not in final_projects:
            final_projects.append(p_clean)

    if not final_projects:
        matches = re.findall(r'(?:Project|System|App|Platform|Dashboard|Model|Website):?\s*([^\n]+)', text, re.IGNORECASE)
        final_projects = [re.sub(r'\s+', ' ', m).strip() for m in matches[:4] if len(m.strip()) > 5]

    return final_projects if final_projects else ["Not explicitly listed"]

def parse_experience(text):
    exp = []
    lines = text.split('\n')
    in_exp = False
    section_end_pattern = r'^\s*(?:education|projects|key\s+projects|academic\s+projects|certifications?|courses?|skills|technical\s+skills|achievements?|awards?|extracurricular|activities|publications?|languages?|interests?|hobbies|declaration|references?|profile|summary|objective)\b'

    for line in lines:
        clean = line.strip()
        if not clean:
            continue
        if re.search(r'^\s*(?:experience|work\s+experience|internships?|employment\s+history|work\s+history)\b', clean, re.IGNORECASE):
            in_exp = True
            continue
        elif in_exp and re.search(section_end_pattern, clean, re.IGNORECASE):
            in_exp = False
            break

        if in_exp and len(clean) > 5:
            exp.append(clean)

    return exp[:5] if exp else ["No formal work experience listed"]

def parse_certifications(text):
    certs = []
    matches = re.findall(r'(Certified|Certification|Course|Certificate|AWS Certified|Google|Coursera|Udemy|NPTEL)[^\n,.]+', text, re.IGNORECASE)
    for m in matches:
        if len(m.strip()) > 5:
            certs.append(m.strip())
    return list(set(certs)) if certs else ["Not found"]

def parse_achievements(text):
    achievements = []
    lines = text.split('\n')
    for line in lines:
        clean = line.strip()
        if re.search(r'\b(awarded|won|1st place|2nd place|finalist|rank|published|patent|hackerRank|leetcode|codechef)\b', clean, re.IGNORECASE):
            achievements.append(clean)
    return achievements[:4] if achievements else ["None explicitly highlighted"]

def parse_resume(filepath, file_type):
    """Main parsing orchestrator returning structured dictionary."""
    text = extract_text(filepath, file_type)
    
    if not text or len(text.strip()) < 30:
        return {
            'error': True,
            'message': 'The document contains no extractable text. It may be scanned, image-only, password-protected, or empty. Please upload a readable text-based PDF or DOCX file.',
            'raw_text': ''
        }

    full_name = parse_name(text)
    email = parse_email(text)
    phone = parse_phone(text)
    links = parse_links(text)
    edu = parse_education(text)
    cgpa = parse_yearwise_cgpa(text)
    skills = parse_skills(text)
    projects = parse_projects(text)
    experience = parse_experience(text)
    certifications = parse_certifications(text)
    achievements = parse_achievements(text)

    return {
        'error': False,
        'full_name': full_name,
        'email': email,
        'phone': phone,
        'links': links,
        'education_degree': edu['degree'],
        'university': edu['university'],
        'graduation_year': edu['grad_year'],
        'cgpa_y1': cgpa['cgpa_y1'],
        'cgpa_y2': cgpa['cgpa_y2'],
        'cgpa_y3': cgpa['cgpa_y3'],
        'cgpa_y4': cgpa['cgpa_y4'],
        'overall_cgpa': cgpa['overall_cgpa'],
        'cgpa_status_y1': cgpa['cgpa_status_y1'],
        'cgpa_status_y2': cgpa['cgpa_status_y2'],
        'cgpa_status_y3': cgpa['cgpa_status_y3'],
        'cgpa_status_y4': cgpa['cgpa_status_y4'],
        'skills': skills,
        'projects': projects,
        'experience': experience,
        'certifications': certifications,
        'achievements': achievements,
        'raw_text': text
    }
