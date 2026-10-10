import os
import json
import werkzeug.utils
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, send_file
from config import Config
import database as db
import resume_parser
import analyzer
import report_generator
from create_sample import create_sample_files

app = Flask(__name__)
app.config.from_object(Config)

# Initialize Database & Sample Files on startup
with app.app_context():
    db.init_db()
    create_sample_files()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    all_resumes = db.get_all_saved_resumes()
    latest_resume = None
    if all_resumes:
        latest_analysis = db.get_full_analysis(all_resumes[0]['id'])
        if latest_analysis:
            latest_resume = latest_analysis

    return render_template('dashboard.html', all_resumes=all_resumes, latest=latest_resume)

@app.route('/upload')
def upload():
    return render_template('upload.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    target_role = request.form.get('target_role', 'Python Developer')

    # Check if user clicked "Try Sample Resume"
    if 'use_sample' in request.form or 'file' not in request.files:
        sample_pdf = os.path.join(Config.SAMPLE_FOLDER, 'sample_resume.pdf')
        if not os.path.exists(sample_pdf):
            create_sample_files()
        
        parsed_data = resume_parser.parse_resume(sample_pdf, 'pdf')
        if parsed_data.get('error'):
            flash(parsed_data['message'], 'danger')
            return redirect(url_for('upload'))

        resume_id = db.save_resume_record("sample_resume.pdf", sample_pdf, "pdf", os.path.getsize(sample_pdf), is_sample=1)
        db.save_extracted_info(resume_id, parsed_data)
        
        cgpa_data = {
            'cgpa_y1': parsed_data.get('cgpa_y1', '8.2'),
            'cgpa_y2': parsed_data.get('cgpa_y2', '8.5'),
            'cgpa_y3': parsed_data.get('cgpa_y3', 'Pending'),
            'cgpa_y4': parsed_data.get('cgpa_y4', 'Pending'),
            'overall_cgpa': parsed_data.get('overall_cgpa', '8.35')
        }
        db.save_education_cgpa(resume_id, cgpa_data)

        analysis = analyzer.analyze_resume_full(parsed_data, cgpa_data, target_role)
        db.save_analysis_result(resume_id, analysis)

        flash("Sample resume analyzed successfully!", "success")
        return redirect(url_for('results', resume_id=resume_id))

    file = request.files['file']
    if file.filename == '':
        flash('No file selected. Please select a PDF or DOCX file.', 'warning')
        return redirect(url_for('upload'))

    if not allowed_file(file.filename):
        flash('Unsupported file format. Please upload a valid .pdf or .docx document.', 'danger')
        return redirect(url_for('upload'))

    filename = werkzeug.utils.secure_filename(file.filename)
    filepath = os.path.join(Config.UPLOAD_FOLDER, filename)
    file.save(filepath)

    file_type = filename.rsplit('.', 1)[1].lower()
    file_size = os.path.getsize(filepath)

    parsed_data = resume_parser.parse_resume(filepath, file_type)
    
    if parsed_data.get('error'):
        # Delete unreadable file
        try: os.remove(filepath)
        except Exception: pass
        flash(parsed_data['message'], 'danger')
        return redirect(url_for('upload'))

    resume_id = db.save_resume_record(filename, filepath, file_type, file_size, is_sample=0)
    db.save_extracted_info(resume_id, parsed_data)

    cgpa_data = {
        'cgpa_y1': parsed_data.get('cgpa_y1', 'Pending'),
        'cgpa_y2': parsed_data.get('cgpa_y2', 'Pending'),
        'cgpa_y3': parsed_data.get('cgpa_y3', 'Pending'),
        'cgpa_y4': parsed_data.get('cgpa_y4', 'Pending'),
        'overall_cgpa': parsed_data.get('overall_cgpa', 'Not calculated')
    }
    db.save_education_cgpa(resume_id, cgpa_data)

    analysis = analyzer.analyze_resume_full(parsed_data, cgpa_data, target_role)
    db.save_analysis_result(resume_id, analysis)

    flash("Resume uploaded and analyzed successfully!", "success")
    return redirect(url_for('results', resume_id=resume_id))

@app.route('/try_sample')
def try_sample():
    sample_pdf = os.path.join(Config.SAMPLE_FOLDER, 'sample_resume.pdf')
    if not os.path.exists(sample_pdf):
        create_sample_files()
    
    parsed_data = resume_parser.parse_resume(sample_pdf, 'pdf')
    resume_id = db.save_resume_record("sample_resume.pdf", sample_pdf, "pdf", os.path.getsize(sample_pdf), is_sample=1)
    db.save_extracted_info(resume_id, parsed_data)
    
    cgpa_data = {
        'cgpa_y1': parsed_data.get('cgpa_y1', '8.2'),
        'cgpa_y2': parsed_data.get('cgpa_y2', '8.5'),
        'cgpa_y3': parsed_data.get('cgpa_y3', 'Pending'),
        'cgpa_y4': parsed_data.get('cgpa_y4', 'Pending'),
        'overall_cgpa': parsed_data.get('overall_cgpa', '8.35')
    }
    db.save_education_cgpa(resume_id, cgpa_data)

    analysis = analyzer.analyze_resume_full(parsed_data, cgpa_data, "Python Developer")
    db.save_analysis_result(resume_id, analysis)

    flash("Demonstration Sample Resume Analyzed Successfully!", "success")
    return redirect(url_for('results', resume_id=resume_id))

@app.route('/results/<int:resume_id>')
def results(resume_id):
    full_data = db.get_full_analysis(resume_id)
    if not full_data:
        flash("Analysis record not found.", "warning")
        return redirect(url_for('dashboard'))

    return render_template('results.html', data=full_data, roles=analyzer.TARGET_ROLES)

@app.route('/edit_details/<int:resume_id>', methods=['POST'])
def edit_details(resume_id):
    skills_raw = request.form.get('skills', '')
    skills_list = [s.strip() for s in skills_raw.split(',') if s.strip()]

    updated_fields = {
        'full_name': request.form.get('full_name'),
        'email': request.form.get('email'),
        'phone': request.form.get('phone'),
        'education_degree': request.form.get('education_degree'),
        'university': request.form.get('university'),
        'graduation_year': request.form.get('graduation_year'),
        'skills': skills_list
    }
    
    db.update_extracted_info(resume_id, updated_fields)
    
    # Re-run analysis with updated information
    full_data = db.get_full_analysis(resume_id)
    new_analysis = analyzer.analyze_resume_full(full_data['extracted'], full_data['cgpa'], full_data['analysis']['target_role'])
    db.save_analysis_result(resume_id, new_analysis)

    flash("Candidate details updated and score re-calculated!", "success")
    return redirect(url_for('results', resume_id=resume_id))

@app.route('/update_cgpa/<int:resume_id>', methods=['POST'])
def update_cgpa(resume_id):
    cgpa_fields = {
        'cgpa_y1': request.form.get('cgpa_y1', 'Pending'),
        'cgpa_y2': request.form.get('cgpa_y2', 'Pending'),
        'cgpa_y3': request.form.get('cgpa_y3', 'Pending'),
        'cgpa_y4': request.form.get('cgpa_y4', 'Pending'),
        'overall_cgpa': request.form.get('overall_cgpa', 'Not calculated')
    }

    db.update_education_cgpa(resume_id, cgpa_fields)

    # Re-run analysis
    full_data = db.get_full_analysis(resume_id)
    new_analysis = analyzer.analyze_resume_full(full_data['extracted'], full_data['cgpa'], full_data['analysis']['target_role'])
    db.save_analysis_result(resume_id, new_analysis)

    flash("Academic CGPA records updated successfully!", "success")
    return redirect(url_for('results', resume_id=resume_id))

@app.route('/api/target_role_analysis', methods=['POST'])
def api_target_role_analysis():
    req = request.get_json()
    resume_id = req.get('resume_id')
    target_role = req.get('target_role', 'Python Developer')

    full_data = db.get_full_analysis(resume_id)
    if not full_data:
        return jsonify({'error': 'Record not found'}), 404

    # Re-evaluate role match & analysis
    new_analysis = analyzer.analyze_resume_full(full_data['extracted'], full_data['cgpa'], target_role)
    db.save_analysis_result(resume_id, new_analysis)

    return jsonify({
        'success': True,
        'analysis': new_analysis
    })

@app.route('/history')
def history():
    resumes = db.get_all_saved_resumes()
    return render_template('history.html', resumes=resumes)

@app.route('/delete/<int:resume_id>', methods=['POST'])
def delete_resume(resume_id):
    db.delete_resume_record(resume_id)
    flash("Resume record deleted successfully.", "info")
    return redirect(url_for('history'))

@app.route('/profile')
def profile():
    user_prof = db.get_user_profile()
    return render_template('profile.html', profile=user_prof)

@app.route('/update_profile', methods=['POST'])
def update_profile():
    profile_data = {
        'full_name': request.form.get('full_name'),
        'email': request.form.get('email'),
        'phone': request.form.get('phone'),
        'university': request.form.get('university'),
        'degree': request.form.get('degree'),
        'graduation_year': request.form.get('graduation_year'),
        'cgpa_y1': request.form.get('cgpa_y1'),
        'cgpa_y2': request.form.get('cgpa_y2'),
        'cgpa_y3': request.form.get('cgpa_y3'),
        'cgpa_y4': request.form.get('cgpa_y4'),
        'overall_cgpa': request.form.get('overall_cgpa'),
        'preferred_role': request.form.get('preferred_role'),
        'interests': request.form.get('interests')
    }
    db.update_user_profile(profile_data)
    flash("Local demo profile updated successfully!", "success")
    return redirect(url_for('profile'))

@app.route('/download_report/<int:resume_id>')
def download_report(resume_id):
    full_data = db.get_full_analysis(resume_id)
    if not full_data:
        flash("Cannot generate report: Record not found.", "danger")
        return redirect(url_for('dashboard'))

    report_filename = f"ResumeReady_Report_{resume_id}.pdf"
    output_path = os.path.join(Config.UPLOAD_FOLDER, report_filename)

    try:
        report_generator.generate_pdf_report(full_data, output_path)
        return send_file(output_path, as_attachment=True, download_name=report_filename)
    except Exception as e:
        flash(f"Report generation error: {str(e)}", "danger")
        return redirect(url_for('results', resume_id=resume_id))

@app.errorhandler(413)
def request_entity_too_large(error):
    flash('File size exceeds maximum allowed limit of 10 MB. Please upload a smaller resume file.', 'danger')
    return redirect(url_for('upload'))

@app.errorhandler(404)
def page_not_found(error):
    return render_template('index.html'), 404

if __name__ == '__main__':
    app.run(debug=True, port=5000)
