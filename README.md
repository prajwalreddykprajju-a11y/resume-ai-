# ResumeReady.AI — AI-Powered Resume Parser & Career Analytics Platform

**ResumeReady.AI** is a full-stack web application designed for college project demonstrations and career readiness. It enables job seekers and students to upload their resumes (PDF/DOCX), parse extracted text, receive an explainable ATS-style score out of 100%, track year-wise B.Tech CGPAs, analyze target job role skill gaps, apply personalized AI recommendations, and download structured PDF reports.

---

## 🌟 Key Features

1. **Multi-Format Text Extraction:** Parses PDF documents using **PyMuPDF** (`fitz`) and DOCX files using **python-docx**, with graceful error handling for unreadable or scanned files.
2. **Explainable ATS Readiness Score (0–100%):** Transparent scoring model based on 6 weighted criteria:
   - Document Structure & Readability (15%)
   - Technical & Domain Skills (25%)
   - Education Completeness & Performance (15%)
   - Projects & Practical Experience (25%)
   - Target Role Keyword Match (10%)
   - Achievements & Quantified Metrics (10%)
3. **Four-Year B.Tech CGPA Tracking:** Dedicated academic section storing Year 1, Year 2, Year 3, Year 4 CGPAs separately alongside completed vs. pending statuses and user-confirmed overall CGPA.
4. **Target Role Skill Gap Analysis:** Compares candidate skills against job descriptions for target roles (*Python Developer, Data Analyst, AI/ML Intern, Business Analyst, Junior Data Science Intern, Full Stack Developer, DevOps Intern*).
5. **Verified Strengths & Actionable Improvements:** Identifies genuine strengths backed by resume evidence and highlights specific areas requiring attention.
6. **Personalized AI Suggestions & Sample Rewrites:** Generates tailored improvement recommendations with sample rewrite snippets.
7. **Persistent SQLite Database Storage:** Stores resume metadata, extracted information, academic CGPAs, and analysis history locally.
8. **Downloadable PDF Analysis Report:** Generates clean, publication-ready PDF reports using **ReportLab**.
9. **Pre-loaded Demonstration Sample Resume:** Allows instant presentation testing with one click without uploading personal files.

---

## 🛠️ Technology Stack

- **Frontend:** HTML5, CSS3, Bootstrap 5, JavaScript, Chart.js
- **Backend:** Python 3.12, Flask Web Framework
- **Database:** SQLite Relational Database
- **Parsing:** PyMuPDF (`fitz`), python-docx
- **NLP & Analysis:** Python regex pattern engine, scikit-learn (TF-IDF & Cosine Similarity)
- **PDF Report Generation:** ReportLab Engine
- **Testing:** Pytest Suite

---

## 📁 Project Structure

```
ResumeReady.AI/
├── app.py                      # Flask Application Entry Point & Routes
├── config.py                   # Configuration Settings & Scoring Weights
├── database.py                 # SQLite Database Management & Helper Methods
├── resume_parser.py            # Document Parsing & Text Extraction Engine
├── analyzer.py                 # ATS Scoring & Skill Gap Analysis Engine
├── report_generator.py         # ReportLab PDF Report Generator
├── create_sample.py            # Pre-loaded Sample Resume Data Generator
├── requirements.txt            # Python Dependencies List
├── vercel.json                 # Vercel Function Configuration
├── README.md                   # Project Documentation
├── .gitignore                  # Git Exclusion Rules
├── sample_data/
│   ├── sample_resume.pdf       # Demonstration Sample Resume (PDF)
│   └── sample_resume.txt       # Demonstration Sample Resume (Text)
├── uploads/                    # Physical Upload Storage Directory
├── instance/
│   └── resumeready.db          # Persistent SQLite Database File
├── tests/                      # Pytest Automated Test Suite
│   ├── __init__.py
│   ├── test_analyzer.py        # Analyzer & Report Generator Tests
│   ├── test_parser.py          # Document Parser & Regex Tests
│   └── test_routes.py          # Flask Integration Route Tests
├── public/
│   └── static/
│       ├── css/
│       │   └── style.css       # Custom Blue & White SaaS Theme Styles
│       └── js/
│           └── main.js         # Drag & Drop, File Validation & Dynamic AJAX
└── templates/
    ├── base.html               # Shared Base Navigation & Footer Layout
    ├── index.html              # Page 1: SaaS Homepage with Walkthrough Modal
    ├── upload.html             # Page 2: Drag & Drop Resume Upload Page
    ├── results.html            # Page 3: Analysis Results & Edit Details Modal
    ├── dashboard.html          # Page 4: User Career & Analytics Dashboard
    ├── history.html            # Page 5: Saved Resumes & Deletion History
    └── profile.html            # Page 6: Editable Local Student Demo Profile
```

---

## 🚀 Quick Start & Installation Guide (Windows)

### Prerequisites
- Python 3.10+ installed on Windows (`py --version`)
- Git (`git --version`)

### Step 1: Open Terminal & Navigate to Project Directory
```powershell
cd "C:\Users\Prajwal Reddy\.gemini\antigravity\scratch\ResumeReady.AI"
```

### Step 2: Create & Activate Python Virtual Environment
```powershell
py -m venv .venv
.\.venv\Scripts\activate
```

### Step 3: Upgrade Pip & Install Requirements
```powershell
py -m pip install --upgrade pip
pip install -r requirements.txt
```

### Step 4: Run the Flask Application
```powershell
python app.py
```

### Step 5: Open Application in Browser
Open your browser and navigate to:
```
http://127.0.0.1:5000
```

---

## ☁️ Deploying to Vercel

1. Import this GitHub repository into Vercel and keep the project root as the **Root Directory**.
2. Vercel detects the Flask application from `app.py`; no custom build command is required.
3. In **Project Settings → Environment Variables**, add `SECRET_KEY` with a long, randomly generated value.
4. Deploy the project.

Vercel serves the CSS and JavaScript from `public/static/`. The app writes its SQLite database and uploaded files under `/tmp` on Vercel. This is suitable for a demo only: that storage is temporary, can be cleared between invocations, and is not shared reliably across function instances. Use a hosted database and object storage if resume history and uploads must persist.

---

## 🚀 Deploying to Render

This repository includes a `render.yaml` Blueprint. In Render, create a **New Blueprint Instance** and connect this GitHub repository. Render will install `requirements.txt`, run the Flask app with Gunicorn, and generate a `SECRET_KEY` for the service automatically. Once deployment finishes, open the service's `onrender.com` URL.

The included free service uses its local filesystem for SQLite data and uploaded files. That filesystem is temporary, so data may be lost when the service restarts or redeploys. For persistent production data, use a hosted database and object storage; a persistent disk is another option for a single Render instance on a plan that supports disks.

---

## 🧪 Running Automated Unit & Integration Tests

Run the complete test suite with `pytest`:
```powershell
.\.venv\Scripts\python -m pytest tests/ -v
```

Output:
```
============================= test session starts =============================
collected 11 items

tests/test_analyzer.py ::: PASSED
tests/test_parser.py ::: PASSED
tests/test_routes.py ::: PASSED

============================= 11 passed in 3.31s ==============================
```

---

## 📊 Explainable ATS Scoring Model

The ATS score is calculated out of 100 points using the following documented weights:

| Category | Weight | Description |
| :--- | :---: | :--- |
| **Structure & Readability** | 15% | Word count (150+ words), clean formatting, extractable contact details. |
| **Technical & Domain Skills** | 25% | Number of verified programming, database, framework & tool skills. |
| **Education Completeness** | 15% | Degree, university name, graduation year, and year-wise CGPA details. |
| **Projects & Practical Exp.** | 25% | Presence and count of capstone projects and internship/work experience. |
| **Target Role Keywords** | 10% | Keyword match percentage against the selected target position dataset. |
| **Achievements & Metrics** | 10% | Certifications, hackathon awards, and quantified numerical impact metrics. |

---

## 🔒 Limitations & Disclaimers

1. **Scanned & Image PDFs:** The application parses text-based PDFs and DOCX files. Image-only scanned PDFs without extractable text will prompt the user to upload a text-based document.
2. **Project Estimate:** The ATS readiness score is our project's explainable estimate and not an official score from commercial recruiters or enterprise ATS providers.
3. **Local Demo Profile:** The profile system runs in local session mode suitable for college project evaluation without external authentication.

---

## 📦 GitHub Repository Setup Commands

To initialize git, commit files, and push to your GitHub repository:

```powershell
# 1. Initialize Git Repository
git init

# 2. Add All Files
git add .

# 3. Create Initial Commit
git commit -m "Initial commit: ResumeReady.AI complete full-stack application"

# 4. Link Remote GitHub Repository (Replace with your actual GitHub repo URL)
git branch -M main
git remote add origin https://github.com/your-username/ResumeReady.AI.git

# 5. Push to GitHub
git push -u origin main
```
#