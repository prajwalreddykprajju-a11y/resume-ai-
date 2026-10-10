import os
import sys

# Add root project dir to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import resume_parser

def test_parse_email_and_phone():
    sample_text = """
    Rohan Sharma
    Email: rohan.test@gmail.com
    Phone: +91 9876543210
    """
    email = resume_parser.parse_email(sample_text)
    phone = resume_parser.parse_phone(sample_text)
    
    assert email == "rohan.test@gmail.com"
    assert "9876543210" in phone or "+91" in phone

def test_parse_skills():
    sample_text = "Experienced in Python, Flask, SQL, HTML, CSS, JavaScript, and Machine Learning."
    skills = resume_parser.parse_skills(sample_text)
    
    assert "Python" in skills
    assert "Flask" in skills
    assert "SQL" in skills

def test_parse_yearwise_cgpa():
    sample_text = """
    Education: B.Tech Computer Science
    Year 1 CGPA: 8.2
    Year 2 CGPA: 8.5
    Overall CGPA: 8.35
    """
    cgpa = resume_parser.parse_yearwise_cgpa(sample_text)
    assert cgpa['cgpa_y1'] == "8.2"
    assert cgpa['cgpa_y2'] == "8.5"
    assert cgpa['cgpa_y3'] == "Pending"
    assert cgpa['overall_cgpa'] == "8.35"

def test_parse_graduation_year_prioritization():
    # Case 1: Resume with start year (2025-Present) and explicit expected graduation year (2029)
    text1 = """
    EDUCATION
    State Technological University (2025–Present)
    Bachelor of Technology in Computer Science & Engineering
    Expected graduation: 2029
    """
    edu1 = resume_parser.parse_education(text1)
    assert edu1['grad_year'] == "2029"

    # Case 2: Resume with date range (2022 - 2026)
    text2 = """
    EDUCATION
    Bachelor of Engineering in CSE (2022 - 2026)
    State University
    """
    edu2 = resume_parser.parse_education(text2)
    assert edu2['grad_year'] == "2026"

    # Case 3: Resume with explicit Graduation Year label
    text3 = """
    EDUCATION
    B.Tech Computer Science
    Graduation Year: 2027
    """
    edu3 = resume_parser.parse_education(text3)
    assert edu3['grad_year'] == "2027"

def test_parse_projects_no_cross_section_bleeding():
    sample_resume = """
    TECHNICAL SKILLS
    Python, Flask, SQLite, HTML

    PROJECTS
    1. ResumeReady.AI — Automated Resume Parsing Platform
       • Engineered a full-stack web application to parse PDF and DOCX files.
       • Implemented explainable scoring logic based on weighted criteria.

    2. Student Analytics Dashboard
       • Built a data visualization dashboard using Pandas and Matplotlib.

    WORK EXPERIENCE
    Python Developer Intern — TechPulse Solutions
    • Developed REST APIs using Flask.

    CERTIFICATIONS
    AWS Certified Practitioner
    """

    projects = resume_parser.parse_projects(sample_resume)

    # Must find exactly 2 distinct project entries
    assert len(projects) == 2

    # Verify project 1 contains complete text without truncation
    assert "ResumeReady.AI" in projects[0]
    assert "Engineered a full-stack web application" in projects[0]
    assert "scoring logic" in projects[0]

    # Verify project 2 contains complete text
    assert "Student Analytics Dashboard" in projects[1]
    assert "Pandas and Matplotlib" in projects[1]

    # Ensure Work Experience or Certifications text did NOT bleed into projects list
    for p in projects:
        assert "TechPulse Solutions" not in p
        assert "AWS Certified" not in p
        assert "REST APIs" not in p
