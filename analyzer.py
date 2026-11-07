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



def _skill_is_present(skill, extracted_skills, raw_text):
    """Return True only when this specific skill is present in extracted skills or text."""
    normalized_skill = skill.casefold().strip()
    normalized_skills = {item.casefold().strip() for item in extracted_skills if isinstance(item, str)}
    if normalized_skill in normalized_skills:
        return True

    if not isinstance(raw_text, str) or not raw_text.strip():
        return False

    # Match a complete skill phrase without matching it as part of a longer word.
    # Lookarounds also work for skills containing punctuation, e.g. C++, C#, Node.js.
    pattern = r"(?<![A-Za-z0-9])" + re.escape(skill.strip()) + r"(?![A-Za-z0-9])"
    return re.search(pattern, raw_text, flags=re.IGNORECASE) is not None


def calculate_ats_score(extracted_info, cgpa_info, target_role="Python Developer"):
    """
    Calculate an explainable ATS-style score from 0 to 100.
    Uses six weighted categories defined in Config.SCORING_WEIGHTS.
    """

    weights = Config.SCORING_WEIGHTS
    breakdown = {}

    text = extracted_info.get("raw_text", "") or ""
    text_lower = text.lower()

    # Normalize and remove duplicate detected skills
    skills = list(dict.fromkeys(
        str(skill).strip().lower()
        for skill in extracted_info.get("skills", [])
        if skill and str(skill).strip()
    ))

    projects = extracted_info.get("projects", [])
    experience = extracted_info.get("experience", [])
    certifications = extracted_info.get("certifications", [])
    achievements = extracted_info.get("achievements", [])

    def has_real_entries(items, placeholders):
        if not items:
            return False
        if isinstance(items, str):
            items = [items]

        return any(
            str(item).strip()
            and str(item).strip().lower() not in placeholders
            for item in items
        )

    # --------------------------------------------------
    # 1. Structure & Readability (15 points)
    # --------------------------------------------------

    structure_score = 0
    word_count = len(text.split())

    if word_count >= 150:
        structure_score += 3
    elif word_count >= 80:
        structure_score += 2
    elif word_count >= 40:
        structure_score += 1

    if re.search(r"\b(professional\s+summary|career\s+summary|summary|objective)\b",
                 text_lower):
        structure_score += 2

    if extracted_info.get("email") not in (None, "", "Not found"):
        structure_score += 3

    if extracted_info.get("phone") not in (None, "", "Not found"):
        structure_score += 2

    links = extracted_info.get("links", [])
    if isinstance(links, str):
        links = [links]

    if any(link and link != "Not found" for link in links):
        structure_score += 2

    recognized_sections = [
        r"\beducation\b",
        r"\btechnical\s+skills\b|\bskills\b",
        r"\bprojects?\b",
        r"\bexperience\b|\binternships?\b"
    ]

    section_count = sum(
        bool(re.search(pattern, text_lower))
        for pattern in recognized_sections
    )

    structure_score += min(3, section_count)
    structure_score = min(weights["structure"], structure_score)

    breakdown["structure"] = {
        "score": structure_score,
        "max": weights["structure"],
        "explanation": (
            f"Evaluated {word_count} words, summary, contact details, "
            f"links and section organization. "
            f"Awarded {structure_score}/{weights['structure']} points."
        )
    }

    # --------------------------------------------------
    # 2. Technical & Domain Skills (25 points)
    # --------------------------------------------------

    # Generic soft skills should not inflate technical skill scoring.
    soft_skills = {
        "communication",
        "problem solving",
        "leadership",
        "teamwork",
        "time management",
        "adaptability",
        "creativity",
        "critical thinking"
    }

    technical_skills = [
        skill for skill in skills
        if skill not in soft_skills
    ]

    technical_skill_count = len(technical_skills)

    # Diminishing, explainable points per detected skill.
    skill_score = min(
        weights["skills"],
        math.ceil(technical_skill_count * 1.8)
    )

    breakdown["skills"] = {
        "score": skill_score,
        "max": weights["skills"],
        "explanation": (
            f"Detected {technical_skill_count} distinct technical/domain "
            f"skills. Keyword detection does not independently verify "
            f"proficiency. Awarded {skill_score}/{weights['skills']} points."
        )
    }

    # --------------------------------------------------
    # 3. Education & Academic Details (15 points)
    # --------------------------------------------------

    education_score = 0

    if extracted_info.get("education_degree") not in (
        None, "", "Not found"
    ):
        education_score += 5

    if extracted_info.get("university") not in (
        None, "", "Not found"
    ):
        education_score += 4

    if extracted_info.get("graduation_year") not in (
        None, "", "Not found"
    ):
        education_score += 2

    cgpa_filled = 0

    for key in ["cgpa_y1", "cgpa_y2", "cgpa_y3", "cgpa_y4"]:
        value = cgpa_info.get(key, "Pending")

        if value not in (None, "", "Pending", "Not found"):
            try:
                float(value)
                cgpa_filled += 1
            except (ValueError, TypeError):
                pass

    education_score += cgpa_filled
    education_score = min(weights["education"], education_score)

    breakdown["education"] = {
        "score": education_score,
        "max": weights["education"],
        "explanation": (
            f"Degree, university, graduation year and "
            f"{cgpa_filled} completed yearly CGPA entries "
            f"contributed {education_score}/{weights['education']} points."
        )
    }

    # --------------------------------------------------
    # 4. Projects & Practical Experience (25 points)
    # --------------------------------------------------

    has_projects = has_real_entries(
        projects,
        {"not explicitly listed", "none", "not found"}
    )

    has_experience = has_real_entries(
        experience,
        {"no formal work experience listed", "none", "not found"}
    )

    project_count = (
        len(projects) if isinstance(projects, list)
        and has_projects else int(has_projects)
    )

    experience_count = (
        len(experience) if isinstance(experience, list)
        and has_experience else int(has_experience)
    )

    project_experience_score = 0

    if has_projects:
        project_experience_score += min(15, project_count * 5)

    if has_experience:
        project_experience_score += min(10, experience_count * 5)

    project_experience_score = min(
        weights["projects_experience"],
        project_experience_score
    )

    breakdown["projects_experience"] = {
        "score": project_experience_score,
        "max": weights["projects_experience"],
        "explanation": (
            f"Detected {project_count} project entries and "
            f"{experience_count} experience entries. "
            f"Awarded {project_experience_score}/"
            f"{weights['projects_experience']} points."
        )
    }

    # --------------------------------------------------
    # 5. Target Role Keyword Match (10 points)
    # --------------------------------------------------

    role_data = TARGET_ROLES.get(
        target_role,
        TARGET_ROLES["Python Developer"]
    )

    required_skills = role_data["required_skills"]

    matched_required = [
        skill for skill in required_skills
        if _skill_is_present(skill, skills, text)
    ]

    required_count = len(required_skills)

    match_ratio = (
        len(matched_required) / required_count
        if required_count else 0
    )

    role_keyword_score = round(match_ratio * weights["role_keywords"])

    breakdown["role_keywords"] = {
        "score": role_keyword_score,
        "max": weights["role_keywords"],
        "explanation": (
            f"Matched {len(matched_required)} of {required_count} "
            f"required keywords for {target_role}. "
            f"Awarded {role_keyword_score}/"
            f"{weights['role_keywords']} points."
        )
    }

    # --------------------------------------------------
    # 6. Achievements & Quantified Impact (10 points)
    # --------------------------------------------------

    achievement_score = 0

    has_certifications = has_real_entries(
        certifications,
        {"not found", "none"}
    )

    has_achievements = has_real_entries(
        achievements,
        {"none explicitly highlighted", "not found", "none"}
    )

    if has_certifications:
        achievement_score += 5

    if has_achievements:
        achievement_score += 5

    # Only examine project, experience and achievement descriptions.
    # Contact numbers, graduation years and other resume-wide numbers
    # are deliberately excluded.

    def flatten_text(items):
        if isinstance(items, str):
            return items

        if isinstance(items, list):
            return " ".join(
                str(item) for item in items if item
            )

        return ""

    evidence_text = " ".join([
        flatten_text(projects),
        flatten_text(experience),
        flatten_text(achievements)
    ]).lower()

    metric_pattern = (
        r"\b\d+(?:\.\d+)?\s*%"
        r"|\b\d+(?:,\d{3})+\s*\+?"
        r"|\b\d+(?:\.\d+)?\s*(?:users?|customers?|records?|"
        r"datasets?|transactions?|hours?|days?|months?|years?|"
        r"requests?|projects?)\b"
        r"|\b\d+(?:\.\d+)?\s*x\b"
    )

    impact_pattern = (
        r"\b(improved|increased|reduced|decreased|achieved|"
        r"saved|optimized|accelerated|generated|processed|"
        r"delivered|boosted|grew|raised)\b"
    )

    has_quantified_impact = (
        bool(re.search(metric_pattern, evidence_text))
        and bool(re.search(impact_pattern, evidence_text))
    )

    if has_quantified_impact and achievement_score < 10:
        achievement_score = min(10, achievement_score + 3)

    achievement_score = min(
        weights["achievements"],
        achievement_score
    )

    breakdown["achievements"] = {
        "score": achievement_score,
        "max": weights["achievements"],
        "explanation": (
            f"Certifications, achievements and contextual "
            f"quantified impact evidence contributed "
            f"{achievement_score}/{weights['achievements']} points."
        )
    }

    # --------------------------------------------------
    # Final Score
    # --------------------------------------------------

    total_score = sum(
        item["score"] for item in breakdown.values()
    )

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



    extracted_skills_lower = [s.lower() for s in extracted_skills if isinstance(s, str)]



    matched_req = []

    missing_req = []



    for sk in req_skills:

        if _skill_is_present(sk, extracted_skills_lower, raw_text):

            matched_req.append(sk)

        else:

            missing_req.append(sk)



    matched_opt = []

    for sk in opt_skills:

        if _skill_is_present(sk, extracted_skills_lower, raw_text):

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



    if not re.search(r'(?<!\w)\d+(?:\.\d+)?%|(?<!\w)\d+(?:,\d{3})*(?:\+)?(?!\w)|(?<!\w)\d+(?:\.\d+)?x(?!\w)', text):

        improvements.append("Lack of quantifiable outcomes. Use metrics like 'improved speed by 25%' or 'processed 5,000+ data records'.")



    if len(certs) == 0 or certs[0] == "Not found":

        improvements.append("No certifications or online course credentials detected. Consider completing role-relevant courses.")



    eval_role = evaluate_target_role(skills, text, target_role)

    if eval_role['missing_skills']:

        improvements.append(f"Missing core keywords for {target_role}: Not detected: {', '.join(eval_role['missing_skills'][:3])}.")



    return improvements



def generate_personalized_suggestions(extracted_info, target_role="Python Developer"):
    """
    Generate evidence-based resume improvement suggestions.

    Rules:
    - Do not suggest a missing summary if one already exists.
    - Do not interpret contact details or unrelated numbers as achievements.
    - Only use technologies actually mentioned in the project description.
    - Never invent experience, skills, metrics or project outcomes.
    """

    suggestions = []

    text = extracted_info.get("raw_text", "") or ""
    text_lower = text.lower()

    skills = extracted_info.get("skills", []) or []
    projects = extracted_info.get("projects", []) or []
    degree = extracted_info.get("education_degree", "student")

    if isinstance(skills, str):
        skills = [skills]

    if isinstance(projects, str):
        projects = [projects]

    # --------------------------------------------------
    # 1. Professional Summary
    # --------------------------------------------------

    summary_pattern = (
        r"(?im)^\s*(?:professional\s+summary|career\s+summary|"
        r"summary|profile|career\s+objective|objective)\s*:?\s*$"
    )

    has_summary = bool(re.search(summary_pattern, text))

    if not has_summary:
        valid_skills = [
            str(skill).strip()
            for skill in skills
            if skill and str(skill).strip()
        ]

        top_skills = ", ".join(valid_skills[:3])

        if degree and degree != "Not found":
            education_text = str(degree)
        else:
            education_text = "your academic background"

        if top_skills:
            summary_rewrite = (
                f"Sample Suggestion: Candidate with a background in "
                f"{education_text} and exposure to {top_skills}, "
                f"seeking entry-level {target_role} opportunities. "
                f"Customize this statement to reflect your actual experience."
            )
        else:
            summary_rewrite = (
                f"Sample Suggestion: Write a short professional summary "
                f"highlighting your actual education, skills and interest "
                f"in {target_role}."
            )

        suggestions.append({
            "title": "Add a Targeted Professional Summary",
            "category": "Formatting & Section Structure",
            "issue": "A clearly labelled professional summary was not detected.",
            "recommendation": (
                "Add a concise 2-3 line summary describing your actual "
                "education, relevant skills and career objective."
            ),
            "sample_rewrite": summary_rewrite
        })

    # --------------------------------------------------
    # 2. Project Description & Impact
    # --------------------------------------------------

    valid_projects = [
        str(project).strip()
        for project in projects
        if project
        and str(project).strip().lower() not in {
            "not explicitly listed",
            "none",
            "not found"
        }
    ]

    if valid_projects:

        raw_project = valid_projects[0]

        # Extract a readable project title.
        project_title = (
            raw_project.split("—")[0]
            .split(":")[0]
            .strip()
        )

        if len(project_title) > 55:
            project_title = project_title[:52] + "..."

        # Only include skills that appear in this project description.
        project_lower = raw_project.lower()

        project_technologies = [
            str(skill).strip()
            for skill in skills
            if skill
            and str(skill).strip().lower() in project_lower
        ]

        project_technologies = list(dict.fromkeys(project_technologies))
        technology_text = ", ".join(project_technologies[:4])

        # Inspect numbers ONLY inside the project description.
        # Do not search the entire resume.
        metric_pattern = (
            r"\b\d+(?:\.\d+)?\s*%"
            r"|\b\d+(?:,\d{3})+\s*\+?"
            r"|\b\d+(?:\.\d+)?\s*(?:users?|records?|students?|"
            r"datasets?|transactions?|requests?|clients?)\b"
            r"|\b\d+(?:\.\d+)?\s*x\b"
        )

        action_pattern = (
            r"\b(improved|increased|reduced|decreased|achieved|"
            r"saved|optimized|accelerated|generated|processed|"
            r"delivered|boosted|developed|built)\b"
        )

        has_project_metric = (
            bool(re.search(metric_pattern, raw_project, re.IGNORECASE))
            and bool(re.search(action_pattern, raw_project, re.IGNORECASE))
        )

        if has_project_metric:
            recommendation = (
                "A numerical result appears in your project description. "
                "Make sure it represents a genuine, measurable outcome "
                "and explain how it was achieved."
            )
        else:
            recommendation = (
                "Expand the project description with your actual "
                "responsibilities, implementation details and technologies. "
                "If you measured a result, include the genuine metric."
            )

        # Preserve the candidate's actual project description.
        rewrite_parts = [
            f"Existing project: {raw_project}"
        ]

        if technology_text:
            rewrite_parts.append(
                f"Technologies identified in this project: {technology_text}"
            )

        rewrite_parts.append(
            "[Add your actual responsibilities and verified results here.]"
        )

        suggestions.append({
            "title": "Improve Project Description & Impact",
            "category": "Action & Impact Words",
            "issue": (
                f"Project '{project_title}' can be described with "
                "more specific responsibilities and verified outcomes."
            ),
            "recommendation": recommendation,
            "sample_rewrite": "Sample Suggestion: " + " ".join(rewrite_parts)
        })

    else:
        suggestions.append({
            "title": "Add Practical Projects",
            "category": "Project Section",
            "issue": "No distinct project entry was identified by parsing.",
            "recommendation": (
                "Include genuine academic or personal projects with "
                "their titles, your contribution, technologies and features."
            ),
            "sample_rewrite": (
                "Sample Suggestion: [Project Title] — Describe what you "
                "actually developed, the technologies you used and "
                "the features you implemented."
            )
        })

    # --------------------------------------------------
    # 3. Target Role Keyword Optimization
    # --------------------------------------------------

    role_eval = evaluate_target_role(skills, text, target_role)

    missing_skills = role_eval.get("missing_skills", [])

    if missing_skills:
        missing_text = ", ".join(missing_skills[:3])

        suggestions.append({
            "title": f"Develop {target_role} Skills",
            "category": "ATS Keyword Optimization",
            "issue": (
                f"Some required skills for {target_role} "
                "were not detected in the resume."
            ),
            "recommendation": (
                f"Review these missing skills: {missing_text}. "
                "If you have genuinely acquired or used them, "
                "include them in the appropriate resume sections."
            ),
            "sample_rewrite": (
                "Sample Suggestion: Add relevant skills only after "
                "you have acquired them and can explain or demonstrate "
                "your knowledge."
            )
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
