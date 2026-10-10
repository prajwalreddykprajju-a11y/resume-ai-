import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable, KeepTogether
from reportlab.lib.units import inch

def generate_pdf_report(analysis_full, output_path):
    """
    Generate a professional PDF report using ReportLab based on saved analysis results.
    """
    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()
    
    # Custom Palette
    NAVY = colors.HexColor("#0f172a")
    BLUE = colors.HexColor("#2563eb")
    LIGHT_BLUE = colors.HexColor("#eff6ff")
    GRAY = colors.HexColor("#64748b")
    GREEN = colors.HexColor("#16a34a")
    RED = colors.HexColor("#dc2626")

    # Typography Styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=NAVY
    )
    
    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=GRAY
    )

    section_heading = ParagraphStyle(
        'SectionHeading',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=14,
        leading=18,
        textColor=NAVY,
        spaceBefore=12,
        spaceAfter=6
    )

    body_style = ParagraphStyle(
        'BodyTextCustom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=13,
        textColor=colors.HexColor("#1e293b")
    )

    bold_body = ParagraphStyle(
        'BoldBody',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9.5,
        leading=13,
        textColor=NAVY
    )

    sample_rewrite_style = ParagraphStyle(
        'SampleRewrite',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=9,
        leading=12,
        textColor=colors.HexColor("#1e40af")
    )

    story = []

    filename = analysis_full.get('filename', 'Resume')
    uploaded_at = analysis_full.get('uploaded_at', 'N/A')
    extracted = analysis_full.get('extracted', {})
    cgpa = analysis_full.get('cgpa', {})
    analysis = analysis_full.get('analysis', {})

    # 1. Header Banner
    header_data = [
        [
            Paragraph("<b>ResumeReady.AI</b> — Comprehensive Resume Analysis Report", title_style),
            Paragraph(f"<b>Generated:</b> {uploaded_at[:10]}<br/><b>Target Role:</b> {analysis.get('target_role', 'Python Developer')}", subtitle_style)
        ]
    ]
    t_header = Table(header_data, colWidths=[4.2 * inch, 2.8 * inch])
    t_header.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('ALIGN', (1,0), (1,0), 'RIGHT'),
    ]))
    story.append(t_header)
    story.append(HRFlowable(width="100%", thickness=1.5, color=BLUE, spaceBefore=8, spaceAfter=12))

    # 2. Score Summary Box
    ats_score = analysis.get('ats_score', 0)
    score_color = GREEN if ats_score >= 75 else (colors.HexColor("#d97706") if ats_score >= 60 else RED)

    score_text = Paragraph(f"<font color='{score_color.hexval()}'><b>{ats_score} / 100</b></font>", ParagraphStyle('BigScore', fontName='Helvetica-Bold', fontSize=26, leading=30))
    score_desc = Paragraph("<b>ATS-Style Resume Readiness Score</b><br/><font color='#64748b' size='8'>Project estimate based on explainable weighting model. Not an official ATS certification.</font>", body_style)

    score_table_data = [[score_text, score_desc]]
    score_table = Table(score_table_data, colWidths=[2.0 * inch, 5.0 * inch])
    score_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), LIGHT_BLUE),
        ('PADDING', (0,0), (-1,-1), 10),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#cbd5e1")),
    ]))
    story.append(score_table)
    story.append(Spacer(1, 10))

    # 3. Scoring Breakdown Table
    story.append(Paragraph("1. Explainable ATS Score Breakdown", section_heading))
    breakdown = analysis.get('scoring_breakdown', {})
    
    bd_rows = [
        [Paragraph("<b>Criteria</b>", bold_body), Paragraph("<b>Max Weight</b>", bold_body), Paragraph("<b>Awarded</b>", bold_body), Paragraph("<b>Rationale & Explanation</b>", bold_body)]
    ]
    
    criteria_names = {
        'structure': 'Structure & Readability',
        'skills': 'Technical & Domain Skills',
        'education': 'Education & Academic Details',
        'projects_experience': 'Projects & Practical Experience',
        'role_keywords': 'Target Role Keyword Match',
        'achievements': 'Achievements & Quantified Impact'
    }

    for key, cname in criteria_names.items():
        if key in breakdown:
            item = breakdown[key]
            bd_rows.append([
                Paragraph(cname, body_style),
                Paragraph(f"{item.get('max', 0)}%", body_style),
                Paragraph(f"<b>{item.get('score', 0)}%</b>", body_style),
                Paragraph(item.get('explanation', ''), body_style)
            ])

    bd_table = Table(bd_rows, colWidths=[2.1 * inch, 0.9 * inch, 0.8 * inch, 3.2 * inch])
    bd_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#f1f5f9")),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#e2e8f0")),
        ('PADDING', (0,0), (-1,-1), 5),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ]))
    story.append(bd_table)
    story.append(Spacer(1, 12))

    # 4. Extracted Candidate Information & Education Details
    story.append(Paragraph("2. Extracted Candidate & Academic Profile", section_heading))
    
    info_data = [
        [Paragraph(f"<b>Full Name:</b> {extracted.get('full_name', 'N/A')}", body_style), Paragraph(f"<b>Email:</b> {extracted.get('email', 'N/A')}", body_style)],
        [Paragraph(f"<b>Phone:</b> {extracted.get('phone', 'N/A')}", body_style), Paragraph(f"<b>Graduation Year:</b> {extracted.get('graduation_year', 'N/A')}", body_style)],
        [Paragraph(f"<b>Degree:</b> {extracted.get('education_degree', 'N/A')}", body_style), Paragraph(f"<b>University:</b> {extracted.get('university', 'N/A')}", body_style)]
    ]
    info_table = Table(info_data, colWidths=[3.5 * inch, 3.5 * inch])
    info_table.setStyle(TableStyle([
        ('PADDING', (0,0), (-1,-1), 4),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#f1f5f9")),
    ]))
    story.append(info_table)
    story.append(Spacer(1, 8))

    # Four-Year CGPA Table
    story.append(Paragraph("<b>Four-Year B.Tech CGPA Breakdown:</b>", bold_body))
    cgpa_rows = [
        [Paragraph("<b>Year 1 CGPA</b>", bold_body), Paragraph("<b>Year 2 CGPA</b>", bold_body), Paragraph("<b>Year 3 CGPA</b>", bold_body), Paragraph("<b>Year 4 CGPA</b>", bold_body), Paragraph("<b>Overall CGPA</b>", bold_body)],
        [
            Paragraph(f"{cgpa.get('cgpa_y1', 'Pending')}", body_style),
            Paragraph(f"{cgpa.get('cgpa_y2', 'Pending')}", body_style),
            Paragraph(f"{cgpa.get('cgpa_y3', 'Pending')}", body_style),
            Paragraph(f"{cgpa.get('cgpa_y4', 'Pending')}", body_style),
            Paragraph(f"<b>{cgpa.get('overall_cgpa', 'Not calculated')}</b>", body_style)
        ]
    ]
    cgpa_table = Table(cgpa_rows, colWidths=[1.4 * inch] * 5)
    cgpa_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#eff6ff")),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#bfdbfe")),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('PADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(cgpa_table)
    story.append(Spacer(1, 12))

    # 5. Strengths & Areas to Improve
    story.append(Paragraph("3. Strengths & Areas for Improvement", section_heading))
    
    strengths_list = analysis.get('strengths', [])
    improvements_list = analysis.get('improvements', [])

    st_p = [Paragraph("<b>Verified Resume Strengths:</b>", bold_body)]
    for s in strengths_list:
        st_p.append(Paragraph(f"<font color='#16a34a'>✔</font> {s}", body_style))

    imp_p = [Paragraph("<b>Areas to Improve:</b>", bold_body)]
    for i in improvements_list:
        imp_p.append(Paragraph(f"<font color='#dc2626'>✖</font> {i}", body_style))

    si_table_data = [[st_p, imp_p]]
    si_table = Table(si_table_data, colWidths=[3.5 * inch, 3.5 * inch])
    si_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('PADDING', (0,0), (-1,-1), 6),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#e2e8f0")),
    ]))
    story.append(si_table)
    story.append(Spacer(1, 12))

    # 6. Target Role Skill Gap & Recommendations
    role_matches = analysis.get('role_matches', {})
    story.append(Paragraph(f"4. Target Role Analysis: {role_matches.get('target_role', 'Target Role')}", section_heading))
    
    matched_skills = ", ".join(role_matches.get('matched_skills', [])) or "None detected"
    missing_skills = ", ".join(role_matches.get('missing_skills', [])) or "None — complete match!"
    priority_skills = ", ".join(role_matches.get('priority_skills', [])) or "N/A"

    role_summary_data = [
        [Paragraph("<b>Target Match Score:</b>", bold_body), Paragraph(f"<b>{role_matches.get('match_pct', 0)}% Match</b>", body_style)],
        [Paragraph("<b>Skills Detected:</b>", bold_body), Paragraph(matched_skills, body_style)],
        [Paragraph("<b>Not Detected in Resume:</b>", bold_body), Paragraph(f"<font color='#dc2626'>{missing_skills}</font>", body_style)],
        [Paragraph("<b>Priority Skills to Add:</b>", bold_body), Paragraph(f"<font color='#2563eb'><b>{priority_skills}</b></font>", body_style)]
    ]
    role_summary_table = Table(role_summary_data, colWidths=[2.0 * inch, 5.0 * inch])
    role_summary_table.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
        ('PADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(role_summary_table)
    story.append(Spacer(1, 12))

    # 7. Personalized Suggestions & Sample Rewrites
    story.append(Paragraph("5. Personalized Actionable Recommendations", section_heading))
    suggestions = analysis.get('suggested_rewrites', [])

    for idx, sug in enumerate(suggestions, 1):
        sug_content = [
            Paragraph(f"<b>Suggestion {idx}: {sug.get('title', '')}</b> ({sug.get('category', '')})", bold_body),
            Paragraph(f"<b>Issue:</b> {sug.get('issue', '')}", body_style),
            Paragraph(f"<b>Action:</b> {sug.get('recommendation', '')}", body_style),
            Paragraph(f"<i>{sug.get('sample_rewrite', '')}</i>", sample_rewrite_style)
        ]
        story.append(KeepTogether(sug_content))
        story.append(Spacer(1, 6))

    # Build PDF
    doc.build(story)
    return output_path
