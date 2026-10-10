import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import analyzer
import report_generator

def test_calculate_ats_score():
    extracted = {
        'full_name': 'Rohan Sharma',
        'email': 'rohan@example.com',
        'phone': '+91 9876543210',
        'education_degree': 'B.Tech CSE',
        'university': 'State University',
        'graduation_year': '2026',
        'skills': ['Python', 'Flask', 'SQL', 'Git', 'Pandas'],
        'projects': ['ResumeReady.AI App'],
        'experience': ['Python Developer Intern'],
        'certifications': ['AWS Certified'],
        'achievements': ['1st Place Hackathon'],
        'links': ['https://github.com/test'],
        'raw_text': 'Detailed resume text with word count > 200 words and 88% accuracy metric.'
    }
    cgpa = {
        'cgpa_y1': '8.2',
        'cgpa_y2': '8.5',
        'cgpa_y3': 'Pending',
        'cgpa_y4': 'Pending',
        'overall_cgpa': '8.35'
    }

    score, breakdown = analyzer.calculate_ats_score(extracted, cgpa, "Python Developer")
    assert 0 <= score <= 100
    assert 'structure' in breakdown
    assert 'skills' in breakdown
    assert breakdown['structure']['score'] > 0

def test_evaluate_target_role():
    skills = ['Python', 'SQL', 'Flask', 'Git']
    raw_text = "Python developer with experience in SQL database and Flask REST APIs."
    
    eval_res = analyzer.evaluate_target_role(skills, raw_text, "Python Developer")
    assert eval_res['target_role'] == "Python Developer"
    assert eval_res['match_pct'] > 50
    assert 'Python' in eval_res['matched_skills']

def test_generate_suggestions_no_fabricated_metrics():
    # Candidate resume without any metrics or 30% / 1000+ claims
    extracted = {
        'full_name': 'Ananya Verma',
        'email': 'ananya@example.com',
        'phone': '+91 9876543210',
        'education_degree': 'B.Tech CSE',
        'university': 'Tech Institute',
        'graduation_year': '2026',
        'skills': ['Python', 'Flask', 'SQLite'],
        'projects': ['Resume Parser App - Built a web application using Python and Flask.'],
        'experience': ['No formal work experience listed'],
        'certifications': ['Not found'],
        'achievements': ['None explicitly highlighted'],
        'raw_text': 'Resume Parser App Built a web application using Python and Flask.'
    }

    suggestions = analyzer.generate_personalized_suggestions(extracted, "Python Developer")

    # Verify suggestions list is generated
    assert len(suggestions) > 0

    for sug in suggestions:
        rewrite = sug.get('sample_rewrite', '')
        # Must NEVER invent fabricated metrics like "30%" or "1,000+ test records"
        assert "30%" not in rewrite
        assert "1,000+" not in rewrite
        assert "1000+" not in rewrite
        assert "5,000+" not in rewrite

    # Check project suggestion specifically
    proj_sug = [s for s in suggestions if 'Projects' in s.get('title', '') or 'Quantify' in s.get('title', '')][0]
    # Should advise user to insert their genuine metric rather than supplying fabricated numbers
    assert "Recommendation" in proj_sug['sample_rewrite'] or "Insert your real outcome" in proj_sug['sample_rewrite'] or "No quantifiable metrics" in proj_sug['recommendation']

def test_generate_suggestions_uses_actual_resume_facts():
    # Candidate resume WITH an actual metric (88% accuracy) and specific skills (Python, Pandas)
    extracted = {
        'full_name': 'Rohan Sharma',
        'email': 'rohan@example.com',
        'phone': '+91 9876543210',
        'education_degree': 'B.Tech CSE',
        'university': 'State University',
        'graduation_year': '2026',
        'skills': ['Python', 'Pandas', 'Matplotlib'],
        'projects': ['Student Analytics Dashboard - Built an EDA dashboard achieving 88% accuracy.'],
        'experience': ['Python Intern'],
        'certifications': ['Course Certificate'],
        'achievements': ['Won 1st place'],
        'raw_text': 'Student Analytics Dashboard Built an EDA dashboard achieving 88% accuracy.'
    }

    suggestions = analyzer.generate_personalized_suggestions(extracted, "Data Analyst")
    proj_sug = [s for s in suggestions if 'Projects' in s.get('title', '') or 'Quantify' in s.get('title', '')][0]

    # Verify that the actual metric from the resume (88% accuracy) is used and NO fake 30% is invented
    assert "88%" in proj_sug['sample_rewrite'] or "88%" in proj_sug['recommendation']
    assert "30%" not in proj_sug['sample_rewrite']
    assert "1,000+" not in proj_sug['sample_rewrite']

def test_pdf_report_generation(tmp_path):
    analysis_full = {
        'filename': 'test_resume.pdf',
        'uploaded_at': '2026-10-09 10:00:00',
        'extracted': {
            'full_name': 'Test Candidate',
            'email': 'test@example.com',
            'phone': '+91 9876543210',
            'education_degree': 'B.Tech',
            'university': 'Test Univ',
            'graduation_year': '2026'
        },
        'cgpa': {
            'cgpa_y1': '8.0',
            'cgpa_y2': '8.2',
            'cgpa_y3': 'Pending',
            'cgpa_y4': 'Pending',
            'overall_cgpa': '8.1'
        },
        'analysis': {
            'ats_score': 82,
            'target_role': 'Python Developer',
            'scoring_breakdown': {
                'structure': {'score': 15, 'max': 15, 'explanation': 'Good'},
                'skills': {'score': 20, 'max': 25, 'explanation': 'Solid'}
            },
            'strengths': ['Verified skills'],
            'improvements': ['Add metrics'],
            'role_matches': {
                'target_role': 'Python Developer',
                'match_pct': 85,
                'matched_skills': ['Python', 'SQL'],
                'missing_skills': ['Docker'],
                'priority_skills': ['Docker']
            },
            'suggested_rewrites': [
                {
                    'title': 'Test Suggestion',
                    'category': 'Structure',
                    'issue': 'Sample Issue',
                    'recommendation': 'Sample Action',
                    'sample_rewrite': 'Sample Rewrite Text'
                }
            ]
        }
    }
    output_pdf = tmp_path / "test_report.pdf"
    res = report_generator.generate_pdf_report(analysis_full, str(output_pdf))
    assert os.path.exists(res)
    assert os.path.getsize(res) > 0
