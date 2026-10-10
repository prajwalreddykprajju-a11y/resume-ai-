import math
import re
from config import Config

# Try importing scikit-learn for optional TF-IDF & Cosine Similarity NLP matching
try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

# Target Role Skill Dataset with required, optional skills & descriptions
TARGET_ROLES = {
    'Python Developer': {
        'required_skills': ['Python', 'SQL', 'Git', 'Flask', 'Django', 'REST API'],
        'optional_skills': ['Docker', 'PostgreSQL', 'Redis', 'Unit Testing', 'Linux', 'HTML', 'CSS', 'JavaScript'],
        'description': 'Develop scalable backend services, REST APIs, database queries, and modular Python software architectures.'
    },
    'Data Analyst': {
        'required_skills': ['Python', 'SQL', 'Pandas', 'NumPy', 'Data Analysis', 'Data Visualization'],
        'optional_skills': ['Matplotlib', 'Seaborn', 'Excel', 'Tableau', 'Power BI', 'R', 'Statistics'],
        'description': 'Analyze business datasets, create interactive visual dashboards, query relational databases, and report actionable metrics.'
    },
    'AI/ML Intern': {
        'required_skills': ['Python', 'Machine Learning', 'TensorFlow', 'PyTorch', 'Scikit-Learn', 'Pandas', 'NumPy'],
        'optional_skills': ['Deep Learning', 'Computer Vision', 'OpenCV', 'NLP', 'Transformers', 'Keras', 'Jupyter'],
        'description': 'Train machine learning models, preprocess complex datasets, evaluate model performance metrics, and assist in AI algorithm deployment.'
    },
    'Business Analyst': {
        'required_skills': ['SQL', 'Data Analysis', 'Excel', 'Communication', 'Problem Solving'],
        'optional_skills': ['Python', 'Power BI', 'Tableau', 'Agile', 'Scrum', 'Project Management'],
        'description': 'Bridge technical teams and business stakeholders, gather system requirements, analyze operational data, and optimize workflow efficiency.'
    },
    'Junior Data Science Intern': {
        'required_skills': ['Python', 'SQL', 'Machine Learning', 'Data Analysis', 'Pandas', 'Scikit-Learn'],
        'optional_skills': ['R', 'Deep Learning', 'NLP', 'Big Data', 'Statistics', 'Matplotlib'],
        'description': 'Conduct exploratory data analysis, build predictive statistical models, run hypothesis testing, and present technical findings.'
    },
    'Full Stack Developer': {
        'required_skills': ['JavaScript', 'HTML', 'CSS', 'Python', 'React', 'SQL', 'Git', 'REST API'],
        'optional_skills': ['TypeScript', 'Node.js', 'Bootstrap', 'MongoDB', 'Docker', 'AWS'],
        'description': 'Build responsive front-end user interfaces, engineer robust backend APIs, integrate databases, and deliver end-to-end web applications.'
    },
    'DevOps Intern': {
        'required_skills': ['Git', 'Linux', 'Docker', 'Bash', 'CI/CD'],
        'optional_skills': ['Kubernetes', 'AWS', 'Python', 'Cloud', 'Azure', 'Terraform'],
        'description': 'Automate build pipelines, manage containerized microservices, configure Linux server environments, and monitor application health.'
    }
}

def calculate_ats_score(extracted_info, cgpa_info, target_role="Python Developer"):
    """
    Calculate explainable ATS-style score (0-100) using weighted breakdown.
    Returns: score, breakdown dict, and rationale explanations.
    """
    weights = Config.SCORING_WEIGHTS
    breakdown = {}
    rationale = []

    text = extracted_info.get('raw_text', '')
    skills = [s.lower() for s in extracted_info.get('skills', [])]
    projects = extracted_info.get('projects', [])
    exp = extracted_info.get('experience', [])
    certs = extracted_info.get('certifications', [])
    achieve = extracted_info.get('achievements', [])

    # 1. Structure & Readability (Weight: 15%)
    struct_score = 0
    word_count = len(text.split())
    if word_count > 150: struct_score += 5
    if extracted_info.get('email') != 'Not found': struct_score += 4
    if extracted_info.get('phone') != 'Not found': struct_score += 3
    if len(extracted_info.get('links', [])) > 0 and extracted_info.get('links')[0] != 'Not found': struct_score += 3
    breakdown['structure'] = {
        'score': struct_score,
        'max': weights['structure'],
        'explanation': f'Word count ({word_count} words) and clear contact details section awarded {struct_score}/{weights["structure"]} points.'
    }

    # 2. Technical & Domain Skills (Weight: 25%)
    skills_count = len(skills)
    skill_score = min(25, math.ceil(skills_count * 2.5))
    breakdown['skills'] = {
        'score': skill_score,
        'max': weights['skills'],
        'explanation': f'Identified {skills_count} verified technical & professional skills yielding {skill_score}/{weights["skills"]} points.'
    }

    # 3. Education Completeness & Academic Details (Weight: 15%)
    edu_score = 0
    if extracted_info.get('education_degree') != 'Not found': edu_score += 5
    if extracted_info.get('university') != 'Not found': edu_score += 4
    if extracted_info.get('graduation_year') != 'Not found': edu_score += 2
    
    # Yearly CGPA completeness check
    cgpa_filled = 0
    for key in ['cgpa_y1', 'cgpa_y2', 'cgpa_y3', 'cgpa_y4']:
        val = cgpa_info.get(key, 'Pending')
        if val != 'Pending' and val != '':
            cgpa_filled += 1
    if cgpa_filled >= 1: edu_score += 4

    breakdown['education'] = {
        'score': edu_score,
        'max': weights['education'],
        'explanation': f'Education degree, university, and year-wise academic records awarded {edu_score}/{weights["education"]} points.'
    }

    # 4. Projects & Practical Experience (Weight: 25%)
    proj_exp_score = 0
    has_projects = len(projects) > 0 and projects[0] != "Not explicitly listed"
    has_exp = len(exp) > 0 and exp[0] != "No formal work experience listed"

    if has_projects:
        proj_exp_score += min(15, len(projects) * 5)
    if has_exp:
        proj_exp_score += min(10, len(exp) * 5)
    
    # Cap at 25
    proj_exp_score = min(25, proj_exp_score)
    breakdown['projects_experience'] = {
        'score': proj_exp_score,
        'max': weights['projects_experience'],
        'explanation': f'Practical evidence in projects ({len(projects) if has_projects else 0}) and internships/experience ({len(exp) if has_exp else 0}) earned {proj_exp_score}/{weights["projects_experience"]} points.'
    }

    # 5. Target Role Keywords Match (Weight: 10%)
    role_data = TARGET_ROLES.get(target_role, TARGET_ROLES['Python Developer'])
    req_skills = [s.lower() for s in role_data['required_skills']]
    matched_req = [s for s in req_skills if s in skills or any(s in text.lower() for s in skills)]
    
    match_ratio = len(matched_req) / max(1, len(req_skills))
    role_kw_score = round(match_ratio * 10)
    breakdown['role_keywords'] = {
        'score': role_kw_score,
        'max': weights['role_keywords'],
        'explanation': f'Matched {len(matched_req)} of {len(req_skills)} essential keywords for target role ({target_role}), giving {role_kw_score}/{weights["role_keywords"]} points.'
    }

    # 6. Achievements & Measurable Outcomes (Weight: 10%)
    achieve_score = 0
    has_certs = len(certs) > 0 and certs[0] != "Not found"
    has_achieve = len(achieve) > 0 and achieve[0] != "None explicitly highlighted"

    if has_certs: achieve_score += 5
    if has_achieve: achieve_score += 5
    
    # Check for quantitative numbers (e.g. 95%, 10k+, 500 users)
    metrics_count = len(re.findall(r'\b\d+%\b|\b\d+\+\b|\b\d+x\b', text))
    if metrics_count > 0 and achieve_score < 10:
        achieve_score = min(10, achieve_score + 3)

    breakdown['achievements'] = {
        'score': achieve_score,
        'max': weights['achievements'],
        'explanation': f'Certifications, achievements, and quantified impact metrics contributed {achieve_score}/{weights["achievements"]} points.'
    }

    # Total Score Calculation
    total_score = sum(b['score'] for b in breakdown.values())
    total_score = max(0, min(100, total_score))

    return total_score, breakdown

def evaluate_target_role(extracted_skills, raw_text, target_role="Python Developer"):
    """
    Compare resume skills against target role dataset.
    Returns matched skills, missing skills, match percentage, and explanation.
    """
    role_info = TARGET_ROLES.get(target_role, TARGET_ROLES['Python Developer'])
    req_skills = role_info['required_skills']
    opt_skills = role_info['optional_skills']

    extracted_skills_lower = [s.lower() for s in extracted_skills]
    text_lower = raw_text.lower()

    matched_req = []
    missing_req = []

    for sk in req_skills:
        if sk.lower() in extracted_skills_lower or re.search(r'\b' + re.escape(sk.lower()) + r'\b', text_lower):
            matched_req.append(sk)
        else:
            missing_req.append(sk)

    matched_opt = []
    for sk in opt_skills:
        if sk.lower() in extracted_skills_lower or re.search(r'\b' + re.escape(sk.lower()) + r'\b', text_lower):
            matched_opt.append(sk)

    # Match % calculation
    req_weight = 0.8
    opt_weight = 0.2
    
    req_match_pct = (len(matched_req) / len(req_skills)) if req_skills else 0
    opt_match_pct = (len(matched_opt) / len(opt_skills)) if opt_skills else 0
    
    total_match_pct = round((req_match_pct * req_weight + opt_match_pct * opt_weight) * 100)

    nlp_similarity = None
    if SKLEARN_AVAILABLE and raw_text:
        try:
            tfidf = TfidfVectorizer(stop_words='english')
            corpus = [raw_text, role_info['description'] + " " + " ".join(req_skills)]
            tfidf_matrix = tfidf.fit_transform(corpus)
            sim = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
            nlp_similarity = round(float(sim) * 100, 1)
        except Exception:
            nlp_similarity = None

    return {
        'target_role': target_role,
        'description': role_info['description'],
        'match_pct': total_match_pct,
        'nlp_similarity': nlp_similarity,
        'matched_skills': matched_req + matched_opt,
        'missing_skills': missing_req,
        'priority_skills': missing_req[:3],
        'explanation': f'Your resume matches {len(matched_req)} of {len(req_skills)} core required skills for {target_role}. Adding priority skills like {", ".join(missing_req[:2]) if missing_req else "advanced domain frameworks"} will increase your competitiveness.'
    }

def generate_recommended_roles(extracted_skills, raw_text):
    """
    Evaluate resume against all roles in TARGET_ROLES dataset and rank them.
    """
    recommended = []
    for role_name in TARGET_ROLES.keys():
        eval_res = evaluate_target_role(extracted_skills, raw_text, role_name)
        recommended.append({
            'role_name': role_name,
            'match_pct': eval_res['match_pct'],
            'matched_skills': eval_res['matched_skills'],
            'missing_skills': eval_res['missing_skills'],
            'explanation': eval_res['explanation']
        })
    
    # Sort by match percentage descending
    recommended.sort(key=lambda x: x['match_pct'], reverse=True)
    return recommended

def identify_strengths(extracted_info, cgpa_info):
    strengths = []
    skills = extracted_info.get('skills', [])
    projects = extracted_info.get('projects', [])
    exp = extracted_info.get('experience', [])
    certs = extracted_info.get('certifications', [])
    achieve = extracted_info.get('achievements', [])
    deg = extracted_info.get('education_degree')

    if len(skills) >= 6:
        strengths.append(f"Strong skill spectrum: Found {len(skills)} technical and domain skills.")
    elif len(skills) > 0:
        strengths.append(f"Solid baseline skills identified: {', '.join(skills[:4])}.")

    if len(projects) > 0 and projects[0] != "Not explicitly listed":
        strengths.append(f"Practical project work highlighted: {len(projects)} distinct projects described.")

    if deg and deg != 'Not found':
        strengths.append(f"Clear degree qualification: {deg} from {extracted_info.get('university', 'University')}.")

    if len(certs) > 0 and certs[0] != "Not found":
        strengths.append(f"Verified learning: {len(certs)} certifications or courses detected.")

    if len(exp) > 0 and exp[0] != "No formal work experience listed":
        strengths.append("Contains relevant internship or work experience.")

    # Check for academic performance
    y1 = cgpa_info.get('cgpa_y1')
    if y1 and y1 != 'Pending':
        strengths.append(f"Structured academic records provided with Year 1 CGPA ({y1}).")

    if not strengths:
        strengths.append("Clear document structure with extractable text.")

    return strengths

def identify_improvements(extracted_info, cgpa_info, target_role="Python Developer"):
    improvements = []
    text = extracted_info.get('raw_text', '')
    skills = extracted_info.get('skills', [])
    projects = extracted_info.get('projects', [])
    certs = extracted_info.get('certifications', [])

    if len(skills) < 5:
        improvements.append("Skill section is sparse. Consider adding technical tools, frameworks, and databases you have used.")

    if len(projects) == 0 or projects[0] == "Not explicitly listed":
        improvements.append("No clear projects section detected. Add 2-3 detailed project descriptions with technologies used.")

    if 'summary' not in text.lower() and 'objective' not in text.lower() and 'profile' not in text.lower():
        improvements.append("Missing a concise Professional Summary at the top of your resume to introduce your background.")

    if not re.search(r'\b\d+%\b|\b\d+\+\b|\b\d+x\b', text):
        improvements.append("Lack of quantifiable outcomes. Use metrics like 'improved speed by 25%' or 'processed 5,000+ data records'.")

    if len(certs) == 0 or certs[0] == "Not found":
        improvements.append("No certifications or online course credentials detected. Consider completing role-relevant courses.")

    eval_role = evaluate_target_role(skills, text, target_role)
    if eval_role['missing_skills']:
        improvements.append(f"Missing core keywords for {target_role}: Not detected: {', '.join(eval_role['missing_skills'][:3])}.")

    return improvements

def generate_personalized_suggestions(extracted_info, target_role="Python Developer"):
    """
    Generate tailored improvement suggestions with sample rewrites clearly marked as suggestions.
    Guarantees:
    - Never invents fake metrics (e.g. 30%, 1000+ records, etc.) or unsupported achievements.
    - Uses strictly tools/technologies/skills and project names present in the candidate's resume.
    - If metrics are missing, instructs the user to add their genuine metrics instead of providing invented numbers.
    """
    suggestions = []
    text = extracted_info.get('raw_text', '')
    skills = extracted_info.get('skills', [])
    projects = extracted_info.get('projects', [])
    deg = extracted_info.get('education_degree', 'student')

    # Suggestion 1: Professional Summary
    if skills:
        top_skills_str = ", ".join(skills[:min(3, len(skills))])
        summary_rewrite = f"Sample Suggestion: Motivated candidate with background in {deg if deg != 'Not found' else 'computer science'} and skills in {top_skills_str}, seeking entry-level {target_role} opportunities."
    else:
        summary_rewrite = f"Sample Suggestion: Motivated candidate aspiring for {target_role} positions with a solid academic foundation in {deg if deg != 'Not found' else 'computer science'}."

    suggestions.append({
        'title': 'Add a Targeted Professional Summary',
        'category': 'Formatting & Section Structure',
        'issue': 'Your resume starts directly with education or contact details without a summary statement.',
        'recommendation': 'Include a 2-3 line summary at the top tailored to your target job role.',
        'sample_rewrite': summary_rewrite
    })

    # Suggestion 2: Project Metric & Impact Enhancement
    if projects and projects[0] != "Not explicitly listed":
        raw_proj = projects[0]
        # Cleanly extract project title/headline (up to 55 chars)
        proj_title = raw_proj.split('—')[0].split(':')[0].split(' Engineered ')[0].split(' Built ')[0].strip()
        if len(proj_title) > 55:
            proj_title = proj_title[:52] + "..."

        # Find actual technologies mentioned in project string or extracted skills
        techs_found = [s for s in skills if s.lower() in raw_proj.lower()]
        tech_str = ", ".join(techs_found[:2]) if techs_found else (", ".join(skills[:2]) if skills else "")

        # Check if the project or resume text contains an actual metric
        existing_metrics = re.findall(r'\b\d+%|\b\d+\+|\b\d+x\b|\b\d+\s*(?:users|records|requests|clients|students)\b', raw_proj, re.IGNORECASE)
        if not existing_metrics:
            existing_metrics = re.findall(r'\b\d+%|\b\d+\+|\b\d+x\b', text, re.IGNORECASE)

        if existing_metrics:
            actual_metric = existing_metrics[0]
            if tech_str:
                rewrite_str = f"Sample Suggestion: Engineered '{proj_title}' using {tech_str}, achieving measurable impact ({actual_metric})."
            else:
                rewrite_str = f"Sample Suggestion: Engineered '{proj_title}', achieving measurable impact ({actual_metric})."
            recommendation_str = f"Your resume mentions metric '{actual_metric}'. Highlight this outcome clearly at the beginning of your project description."
        else:
            if tech_str:
                rewrite_str = f"Sample Suggestion: Built '{proj_title}' using {tech_str}. [Recommendation: Insert your real outcome here, e.g., 'improving speed by X%' or 'handling Y users']."
            else:
                rewrite_str = f"Sample Suggestion: Built '{proj_title}'. [Recommendation: Insert your real outcome here, e.g., 'improving speed by X%' or 'handling Y users']."
            recommendation_str = "No quantifiable metrics were detected in your project. Add genuine measurable outcomes (e.g. latency reduction, user count, dataset size) from your actual work."

        suggestions.append({
            'title': 'Quantify Achievements in Projects',
            'category': 'Action & Impact Words',
            'issue': f"Project description '{proj_title}' can be enhanced with measurable results.",
            'recommendation': recommendation_str,
            'sample_rewrite': rewrite_str
        })
    else:
        suggestions.append({
            'title': 'Add Practical Capstone Projects',
            'category': 'Project Section',
            'issue': 'No distinct project section was identified by parsing.',
            'recommendation': 'Include at least 2 capstone projects with clear titles, tools used, and key features.',
            'sample_rewrite': f"Sample Suggestion: Include a project entry formatted as: '[Project Title] — Developed [Feature] using [Technology]. (Add your genuine metrics, e.g. processed X records or served Y users)'."
        })

    # Suggestion 3: Target Role Keyword Optimization
    role_eval = evaluate_target_role(skills, text, target_role)
    if role_eval['missing_skills']:
        missing_str = ", ".join(role_eval['missing_skills'][:3])
        first_missing = role_eval['missing_skills'][0]
        suggestions.append({
            'title': f'Incorporate {target_role} Target Keywords',
            'category': 'ATS Keyword Optimization',
            'issue': f'Keywords essential for {target_role} are missing or not detected.',
            'recommendation': f'Consider learning and incorporating missing keywords such as {missing_str} into your skills or projects.',
            'sample_rewrite': f"Sample Suggestion: Once acquired, add keywords naturally (e.g., 'Applied {first_missing} for data processing and software development')."
        })

    return suggestions

def analyze_resume_full(extracted_info, cgpa_info, target_role="Python Developer"):
    """
    Main entry point for analyzing parsed resume data.
    """
    score, breakdown = calculate_ats_score(extracted_info, cgpa_info, target_role)
    role_matches = evaluate_target_role(extracted_info.get('skills', []), extracted_info.get('raw_text', ''), target_role)
    recommended_roles = generate_recommended_roles(extracted_info.get('skills', []), extracted_info.get('raw_text', ''))
    strengths = identify_strengths(extracted_info, cgpa_info)
    improvements = identify_improvements(extracted_info, cgpa_info, target_role)
    suggestions = generate_personalized_suggestions(extracted_info, target_role)

    return {
        'ats_score': score,
        'scoring_breakdown': breakdown,
        'target_role': target_role,
        'role_match_pct': role_matches['match_pct'],
        'role_matches': role_matches,
        'recommended_roles': recommended_roles,
        'strengths': strengths,
        'improvements': improvements,
        'suggested_rewrites': suggestions
    }
