import json
from django.shortcuts import render, redirect
from django.utils import timezone

from student.models import Student
from student.logic.authentication import (
    get_logged_in_student,
    is_student_logged_in,
    logout_student,
)
from student.logic.analytics import (
    calculate_placement_readiness,
    get_student_rank,
)
from student.logic.validation import validate_student_profile


def portfolio_editor_view(request):
   
    if not is_student_logged_in(request):
        return redirect('signin_student')

    student = get_logged_in_student(request)
    if not student:
        logout_student(request)
        return redirect('signin_student')

    context = {
        'student': student,
        'completion_percentage': student.profile_completion_percentage,
        'projects_list': student.get_projects_list(),
        'skills_list': student.get_skills_list(),
        'error': None,
        'success': None,
        'active_nav': 'portfolio',
    }

    if request.method == 'POST':
        name = request.POST.get('name', '')
        department = request.POST.get('department', '')
        year = request.POST.get('year', '')
        prn = request.POST.get('prn', '')
        cgpa_raw = request.POST.get('cgpa', '')
        skills = request.POST.get('skills', '')
        certifications = request.POST.get('certifications', '')
        headline = request.POST.get('headline', '')
        summary = request.POST.get('summary', '')
        resume_link = request.POST.get('resume_link', '')
        linkedin_url = request.POST.get('linkedin_url', '')
        github_url = request.POST.get('github_url', '')

        # Handle multiple structured projects
        project_titles = request.POST.getlist('project_title[]')
        if project_titles:
            project_descriptions = request.POST.getlist('project_description[]')
            project_tech = request.POST.getlist('project_tech[]')
            project_github = request.POST.getlist('project_github[]')
            project_live = request.POST.getlist('project_live[]')

            structured_projects = []
            for i, p_title in enumerate(project_titles):
                p_title = p_title.strip()
                if p_title:
                    structured_projects.append({
                        'title': p_title,
                        'description': project_descriptions[i].strip() if i < len(project_descriptions) else '',
                        'tech_stack': project_tech[i].strip() if i < len(project_tech) else '',
                        'github_url': project_github[i].strip() if i < len(project_github) else '',
                        'live_url': project_live[i].strip() if i < len(project_live) else '',
                    })
            if structured_projects:
                projects = json.dumps(structured_projects)
            else:
                projects = request.POST.get('projects', '')
        else:
            projects = request.POST.get('projects', '')

        is_valid, error_msg, cleaned_data = validate_student_profile(
            name=name,
            department=department,
            year=year,
            prn=prn,
            cgpa_raw=cgpa_raw,
            skills=skills,
            certifications=certifications,
            projects=projects,
            resume_link=resume_link,
            linkedin_url=linkedin_url,
            github_url=github_url,
            headline=headline,
            summary=summary,
        )

        if not is_valid:
            context['error'] = error_msg
        else:
            # Handle certificate removal if requested
            if request.POST.get('remove_certificate') == '1':
                if student.certificate_file:
                    try:
                        student.certificate_file.delete(save=False)
                    except Exception:
                        pass
                    student.certificate_file = None

            # Handle certificate file upload
            if 'certificate_file' in request.FILES:
                cert_file = request.FILES['certificate_file']
                allowed_extensions = ('pdf', 'png', 'jpg', 'jpeg')
                file_ext = cert_file.name.rsplit('.', 1)[-1].lower() if '.' in cert_file.name else ''

                if file_ext not in allowed_extensions:
                    context['error'] = "Invalid certificate format. Please upload a PDF, PNG, or JPG/JPEG file."
                    context['projects_list'] = student.get_projects_list()
                    return render(request, 'myportfolio/profile.html', context)

                # 5MB size limit
                if cert_file.size > 5 * 1024 * 1024:
                    context['error'] = "Certificate file size exceeds the 5MB limit. Please upload a smaller file."
                    context['projects_list'] = student.get_projects_list()
                    return render(request, 'myportfolio/profile.html', context)

                # Delete old certificate file if replacing
                if student.certificate_file:
                    try:
                        student.certificate_file.delete(save=False)
                    except Exception:
                        pass

                student.certificate_file = cert_file

            student.name = cleaned_data['name']
            student.department = cleaned_data['department']
            student.year = cleaned_data['year']
            student.prn = cleaned_data['prn']
            student.cgpa = cleaned_data['cgpa']
            student.skills = cleaned_data['skills']
            student.certifications = cleaned_data['certifications']
            student.projects = cleaned_data['projects']
            student.resume_link = cleaned_data['resume_link']
            student.linkedin_url = cleaned_data['linkedin_url']
            student.github_url = cleaned_data['github_url']
            student.headline = cleaned_data['headline']
            student.summary = cleaned_data['summary']
            student.save()

            # Update session stored name
            request.session['student_name'] = student.name
            context['completion_percentage'] = student.profile_completion_percentage
            context['projects_list'] = student.get_projects_list()
            context['skills_list'] = student.get_skills_list()
            context['success'] = f"Portfolio saved successfully! Profile readiness is now {student.profile_completion_percentage}%."

    return render(request, 'myportfolio/profile.html', context)


def portfolio_preview_view(request, student_id=None):
    
    if student_id:
        try:
            student = Student.objects.get(id=student_id)
        except Student.DoesNotExist:
            return redirect('myportfolio:editor')
    else:
        if not is_student_logged_in(request):
            return redirect('signin_student')
        student = get_logged_in_student(request)
        if not student:
            logout_student(request)
            return redirect('signin_student')

    readiness_data = calculate_placement_readiness(student)
    rank_data = get_student_rank(student)
    skills_list = student.get_skills_list()
    projects_list = student.get_projects_list()

    # Parse certifications into structured items
    raw_certs = student.certifications or ""
    cert_lines = [c.strip() for c in raw_certs.replace('\r', '').split('\n') if c.strip()]
    certifications_list = []
    for line in cert_lines:
        if ' - ' in line:
            parts = line.split(' - ', 1)
            certifications_list.append({'name': parts[0].strip(), 'issuer': parts[1].strip()})
        elif ' by ' in line:
            parts = line.split(' by ', 1)
            certifications_list.append({'name': parts[0].strip(), 'issuer': parts[1].strip()})
        else:
            certifications_list.append({'name': line, 'issuer': ''})

    initials = "".join([part[0].upper() for part in student.name.strip().split()[:2]]) if student.name.strip() else "S"
    current_student = get_logged_in_student(request)
    is_owner = bool(current_student and current_student.id == student.id)

    context = {
        'student': student,
        'initials': initials,
        'skills_list': skills_list,
        'projects_list': projects_list,
        'certifications_list': certifications_list,
        'readiness_score': readiness_data['readiness_score'],
        'readiness_band': readiness_data['band'],
        'rank': rank_data['rank'],
        'total_students': rank_data['total_students'],
        'is_owner': is_owner,
        'is_logged_in': bool(current_student),
        'active_nav': 'portfolio',
        'now': timezone.now(),
    }
    return render(request, 'myportfolio/portfolio_preview.html', context)
