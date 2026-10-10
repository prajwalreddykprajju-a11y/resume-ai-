import sqlite3
import os
import json
from datetime import datetime
from config import Config

def get_db_connection():
    os.makedirs(os.path.dirname(Config.DATABASE_PATH), exist_ok=True)
    conn = sqlite3.connect(Config.DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
    os.makedirs(Config.SAMPLE_FOLDER, exist_ok=True)
    os.makedirs(os.path.dirname(Config.DATABASE_PATH), exist_ok=True)
    
    conn = get_db_connection()
    cursor = conn.cursor()

    # Resumes table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS resumes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL,
            filepath TEXT NOT NULL,
            file_type TEXT NOT NULL,
            file_size INTEGER NOT NULL,
            uploaded_at TEXT NOT NULL,
            is_sample INTEGER DEFAULT 0
        )
    ''')

    # Extracted Info table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS extracted_info (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            resume_id INTEGER NOT NULL,
            full_name TEXT,
            email TEXT,
            phone TEXT,
            education_degree TEXT,
            university TEXT,
            graduation_year TEXT,
            skills_json TEXT,
            projects_json TEXT,
            experience_json TEXT,
            certifications_json TEXT,
            achievements_json TEXT,
            links_json TEXT,
            raw_text TEXT,
            FOREIGN KEY (resume_id) REFERENCES resumes(id) ON DELETE CASCADE
        )
    ''')

    # Education & CGPA details table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS education_cgpa (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            resume_id INTEGER NOT NULL,
            cgpa_y1 TEXT DEFAULT 'Pending',
            cgpa_y2 TEXT DEFAULT 'Pending',
            cgpa_y3 TEXT DEFAULT 'Pending',
            cgpa_y4 TEXT DEFAULT 'Pending',
            overall_cgpa TEXT DEFAULT 'Not calculated',
            cgpa_status_y1 TEXT DEFAULT 'Pending',
            cgpa_status_y2 TEXT DEFAULT 'Pending',
            cgpa_status_y3 TEXT DEFAULT 'Pending',
            cgpa_status_y4 TEXT DEFAULT 'Pending',
            overall_cgpa_type TEXT DEFAULT 'user_provided',
            scale REAL DEFAULT 10.0,
            FOREIGN KEY (resume_id) REFERENCES resumes(id) ON DELETE CASCADE
        )
    ''')

    # Analysis Results table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS analysis_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            resume_id INTEGER NOT NULL,
            ats_score INTEGER NOT NULL,
            scoring_breakdown_json TEXT,
            strengths_json TEXT,
            improvements_json TEXT,
            target_role TEXT DEFAULT 'Python Developer',
            role_match_pct INTEGER DEFAULT 0,
            role_matches_json TEXT,
            recommended_roles_json TEXT,
            suggested_rewrites_json TEXT,
            created_at TEXT NOT NULL,
            FOREIGN KEY (resume_id) REFERENCES resumes(id) ON DELETE CASCADE
        )
    ''')

    # User Profile table (Local demo profile)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_profile (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT DEFAULT 'Demo Student',
            email TEXT DEFAULT 'student@example.edu',
            phone TEXT DEFAULT '+91 98765 43210',
            university TEXT DEFAULT 'State Technological University',
            degree TEXT DEFAULT 'B.Tech in Computer Science & Engineering',
            graduation_year TEXT DEFAULT '2026',
            cgpa_y1 TEXT DEFAULT '8.2',
            cgpa_y2 TEXT DEFAULT '8.5',
            cgpa_y3 TEXT DEFAULT 'Pending',
            cgpa_y4 TEXT DEFAULT 'Pending',
            overall_cgpa TEXT DEFAULT '8.35',
            preferred_role TEXT DEFAULT 'Python Developer',
            interests TEXT DEFAULT 'Software Development, AI/ML, Data Analytics'
        )
    ''')

    # Insert default demo profile if empty
    cursor.execute('SELECT COUNT(*) FROM user_profile')
    if cursor.fetchone()[0] == 0:
        cursor.execute('''
            INSERT INTO user_profile (full_name, email, phone, university, degree, graduation_year, cgpa_y1, cgpa_y2, cgpa_y3, cgpa_y4, overall_cgpa, preferred_role, interests)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            'Demo Student', 'student@example.edu', '+91 98765 43210',
            'State Technological University', 'B.Tech in Computer Science & Engineering', '2026',
            '8.2', '8.5', 'Pending', 'Pending', '8.35',
            'Python Developer', 'Software Development, AI/ML, Data Analytics'
        ))

    conn.commit()
    conn.close()

def save_resume_record(filename, filepath, file_type, file_size, is_sample=0):
    conn = get_db_connection()
    cursor = conn.cursor()
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    cursor.execute('''
        INSERT INTO resumes (filename, filepath, file_type, file_size, uploaded_at, is_sample)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (filename, filepath, file_type, file_size, now, is_sample))
    resume_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return resume_id

def save_extracted_info(resume_id, extracted_data):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO extracted_info (
            resume_id, full_name, email, phone, education_degree, university, graduation_year,
            skills_json, projects_json, experience_json, certifications_json, achievements_json, links_json, raw_text
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        resume_id,
        extracted_data.get('full_name', 'Not found'),
        extracted_data.get('email', 'Not found'),
        extracted_data.get('phone', 'Not found'),
        extracted_data.get('education_degree', 'Not found'),
        extracted_data.get('university', 'Not found'),
        extracted_data.get('graduation_year', 'Not found'),
        json.dumps(extracted_data.get('skills', [])),
        json.dumps(extracted_data.get('projects', [])),
        json.dumps(extracted_data.get('experience', [])),
        json.dumps(extracted_data.get('certifications', [])),
        json.dumps(extracted_data.get('achievements', [])),
        json.dumps(extracted_data.get('links', [])),
        extracted_data.get('raw_text', '')
    ))
    conn.commit()
    conn.close()

def save_education_cgpa(resume_id, cgpa_data):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO education_cgpa (
            resume_id, cgpa_y1, cgpa_y2, cgpa_y3, cgpa_y4, overall_cgpa,
            cgpa_status_y1, cgpa_status_y2, cgpa_status_y3, cgpa_status_y4, overall_cgpa_type, scale
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        resume_id,
        cgpa_data.get('cgpa_y1', 'Pending'),
        cgpa_data.get('cgpa_y2', 'Pending'),
        cgpa_data.get('cgpa_y3', 'Pending'),
        cgpa_data.get('cgpa_y4', 'Pending'),
        cgpa_data.get('overall_cgpa', 'Not calculated'),
        cgpa_data.get('cgpa_status_y1', 'Completed' if cgpa_data.get('cgpa_y1') != 'Pending' else 'Pending'),
        cgpa_data.get('cgpa_status_y2', 'Completed' if cgpa_data.get('cgpa_y2') != 'Pending' else 'Pending'),
        cgpa_data.get('cgpa_status_y3', 'Completed' if cgpa_data.get('cgpa_y3') != 'Pending' else 'Pending'),
        cgpa_data.get('cgpa_status_y4', 'Completed' if cgpa_data.get('cgpa_y4') != 'Pending' else 'Pending'),
        cgpa_data.get('overall_cgpa_type', 'user_provided'),
        cgpa_data.get('scale', 10.0)
    ))
    conn.commit()
    conn.close()

def save_analysis_result(resume_id, analysis_data):
    conn = get_db_connection()
    cursor = conn.cursor()
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    cursor.execute('''
        INSERT INTO analysis_results (
            resume_id, ats_score, scoring_breakdown_json, strengths_json, improvements_json,
            target_role, role_match_pct, role_matches_json, recommended_roles_json, suggested_rewrites_json, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        resume_id,
        analysis_data.get('ats_score', 0),
        json.dumps(analysis_data.get('scoring_breakdown', {})),
        json.dumps(analysis_data.get('strengths', [])),
        json.dumps(analysis_data.get('improvements', [])),
        analysis_data.get('target_role', 'Python Developer'),
        analysis_data.get('role_match_pct', 0),
        json.dumps(analysis_data.get('role_matches', {})),
        json.dumps(analysis_data.get('recommended_roles', [])),
        json.dumps(analysis_data.get('suggested_rewrites', [])),
        now
    ))
    conn.commit()
    conn.close()

def get_full_analysis(resume_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM resumes WHERE id = ?', (resume_id,))
    resume = cursor.fetchone()
    if not resume:
        conn.close()
        return None

    cursor.execute('SELECT * FROM extracted_info WHERE resume_id = ?', (resume_id,))
    info = cursor.fetchone()

    cursor.execute('SELECT * FROM education_cgpa WHERE resume_id = ?', (resume_id,))
    cgpa = cursor.fetchone()

    cursor.execute('SELECT * FROM analysis_results WHERE resume_id = ? ORDER BY id DESC LIMIT 1', (resume_id,))
    analysis = cursor.fetchone()

    conn.close()

    if not analysis or not info or not cgpa:
        return None

    # Parse JSON fields safely
    extracted_dict = {
        'full_name': info['full_name'],
        'email': info['email'],
        'phone': info['phone'],
        'education_degree': info['education_degree'],
        'university': info['university'],
        'graduation_year': info['graduation_year'],
        'skills': json.loads(info['skills_json'] or '[]'),
        'projects': json.loads(info['projects_json'] or '[]'),
        'experience': json.loads(info['experience_json'] or '[]'),
        'certifications': json.loads(info['certifications_json'] or '[]'),
        'achievements': json.loads(info['achievements_json'] or '[]'),
        'links': json.loads(info['links_json'] or '[]'),
        'raw_text': info['raw_text']
    }

    cgpa_dict = {
        'cgpa_y1': cgpa['cgpa_y1'],
        'cgpa_y2': cgpa['cgpa_y2'],
        'cgpa_y3': cgpa['cgpa_y3'],
        'cgpa_y4': cgpa['cgpa_y4'],
        'overall_cgpa': cgpa['overall_cgpa'],
        'cgpa_status_y1': cgpa['cgpa_status_y1'],
        'cgpa_status_y2': cgpa['cgpa_status_y2'],
        'cgpa_status_y3': cgpa['cgpa_status_y3'],
        'cgpa_status_y4': cgpa['cgpa_status_y4'],
        'overall_cgpa_type': cgpa['overall_cgpa_type'],
        'scale': cgpa['scale']
    }

    analysis_dict = {
        'ats_score': analysis['ats_score'],
        'scoring_breakdown': json.loads(analysis['scoring_breakdown_json'] or '{}'),
        'strengths': json.loads(analysis['strengths_json'] or '[]'),
        'improvements': json.loads(analysis['improvements_json'] or '[]'),
        'target_role': analysis['target_role'],
        'role_match_pct': analysis['role_match_pct'],
        'role_matches': json.loads(analysis['role_matches_json'] or '{}'),
        'recommended_roles': json.loads(analysis['recommended_roles_json'] or '[]'),
        'suggested_rewrites': json.loads(analysis['suggested_rewrites_json'] or '[]'),
        'created_at': analysis['created_at']
    }

    return {
        'resume_id': resume['id'],
        'filename': resume['filename'],
        'filepath': resume['filepath'],
        'file_type': resume['file_type'],
        'file_size': resume['file_size'],
        'uploaded_at': resume['uploaded_at'],
        'is_sample': resume['is_sample'],
        'extracted': extracted_dict,
        'cgpa': cgpa_dict,
        'analysis': analysis_dict
    }

def get_all_saved_resumes():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT r.id, r.filename, r.file_size, r.uploaded_at, r.is_sample,
               a.ats_score, a.target_role, a.role_match_pct
        FROM resumes r
        LEFT JOIN analysis_results a ON r.id = a.resume_id
        GROUP BY r.id
        ORDER BY r.id DESC
    ''')
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def delete_resume_record(resume_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get filepath first to delete physical file if present
    cursor.execute('SELECT filepath, is_sample FROM resumes WHERE id = ?', (resume_id,))
    row = cursor.fetchone()
    if row and not row['is_sample'] and os.path.exists(row['filepath']):
        try:
            os.remove(row['filepath'])
        except Exception:
            pass

    cursor.execute('DELETE FROM resumes WHERE id = ?', (resume_id,))
    conn.commit()
    conn.close()
    return True

def get_user_profile():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM user_profile LIMIT 1')
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else {}

def update_user_profile(profile_data):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE user_profile SET
            full_name = ?,
            email = ?,
            phone = ?,
            university = ?,
            degree = ?,
            graduation_year = ?,
            cgpa_y1 = ?,
            cgpa_y2 = ?,
            cgpa_y3 = ?,
            cgpa_y4 = ?,
            overall_cgpa = ?,
            preferred_role = ?,
            interests = ?
        WHERE id = 1
    ''', (
        profile_data.get('full_name'),
        profile_data.get('email'),
        profile_data.get('phone'),
        profile_data.get('university'),
        profile_data.get('degree'),
        profile_data.get('graduation_year'),
        profile_data.get('cgpa_y1'),
        profile_data.get('cgpa_y2'),
        profile_data.get('cgpa_y3'),
        profile_data.get('cgpa_y4'),
        profile_data.get('overall_cgpa'),
        profile_data.get('preferred_role'),
        profile_data.get('interests')
    ))
    conn.commit()
    conn.close()

def update_extracted_info(resume_id, updated_fields):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Prepare skills_json if list provided
    skills_json = json.dumps(updated_fields.get('skills', [])) if isinstance(updated_fields.get('skills'), list) else updated_fields.get('skills_json')

    cursor.execute('''
        UPDATE extracted_info SET
            full_name = ?,
            email = ?,
            phone = ?,
            education_degree = ?,
            university = ?,
            graduation_year = ?,
            skills_json = COALESCE(?, skills_json)
        WHERE resume_id = ?
    ''', (
        updated_fields.get('full_name'),
        updated_fields.get('email'),
        updated_fields.get('phone'),
        updated_fields.get('education_degree'),
        updated_fields.get('university'),
        updated_fields.get('graduation_year'),
        skills_json,
        resume_id
    ))
    conn.commit()
    conn.close()

def update_education_cgpa(resume_id, cgpa_fields):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    y1 = cgpa_fields.get('cgpa_y1', 'Pending')
    y2 = cgpa_fields.get('cgpa_y2', 'Pending')
    y3 = cgpa_fields.get('cgpa_y3', 'Pending')
    y4 = cgpa_fields.get('cgpa_y4', 'Pending')
    overall = cgpa_fields.get('overall_cgpa', 'Not calculated')

    cursor.execute('''
        UPDATE education_cgpa SET
            cgpa_y1 = ?,
            cgpa_y2 = ?,
            cgpa_y3 = ?,
            cgpa_y4 = ?,
            overall_cgpa = ?,
            cgpa_status_y1 = ?,
            cgpa_status_y2 = ?,
            cgpa_status_y3 = ?,
            cgpa_status_y4 = ?,
            overall_cgpa_type = 'user_provided'
        WHERE resume_id = ?
    ''', (
        y1, y2, y3, y4, overall,
        'Completed' if y1 != 'Pending' and y1 != '' else 'Pending',
        'Completed' if y2 != 'Pending' and y2 != '' else 'Pending',
        'Completed' if y3 != 'Pending' and y3 != '' else 'Pending',
        'Completed' if y4 != 'Pending' and y4 != '' else 'Pending',
        resume_id
    ))
    conn.commit()
    conn.close()
