# student/logic/analytics.py
#
# WHAT: Placement Readiness Analytics Engine
#
# MODULE PURPOSE:
# 1. Checkpoint 14: Topic-wise and Subject-wise score analysis
# 2. Checkpoint 15: Final Exam vs Subject Exam score segregation
# 3. Checkpoint 16: Placement Readiness Score calculation (Transparent weighted formula)
# 4. Checkpoint 17: Student Ranking system (Descending sort with tie-breaking)
# 5. Checkpoint 18: Weak Area Detection & Actionable Improvement Plan Generation
#
# COLLEGE VIVA RELEVANCE:
# - All calculations use pure Python and Django ORM (no AI/ML black box).
# - Every component of the score is transparent, explainable, and mathematically bounded (0-100).

from typing import Dict, List, Any, Optional
from student.models import Student
from assignments.models import Assignment, Attempt


def get_student_subject_performance(student: Student) -> List[Dict[str, Any]]:
    """
    CHECKPOINT 14: Calculates subject-wise aggregated performance for a student.

    Returns a list of dicts:
    [
        {
            'subject': 'Data Structures',
            'attempts_count': 2,
            'total_score': 15,
            'total_marks': 20,
            'percentage': 75.0,
            'status': 'Good' / 'Moderate' / 'Needs Practice'
        },
        ...
    ]
    """
    completed_attempts = Attempt.objects.filter(
        student=student,
        status='COMPLETED'
    ).select_related('assignment')

    subject_data: Dict[str, Dict[str, Any]] = {}

    for attempt in completed_attempts:
        subj = attempt.assignment.subject.strip() or "General Technical"
        if subj not in subject_data:
            subject_data[subj] = {
                'subject': subj,
                'attempts_count': 0,
                'total_score': 0,
                'total_marks': 0,
            }
        subject_data[subj]['attempts_count'] += 1
        subject_data[subj]['total_score'] += attempt.score
        subject_data[subj]['total_marks'] += attempt.assignment.total_marks

    result = []
    for subj, data in subject_data.items():
        pct = 0.0
        if data['total_marks'] > 0:
            pct = round((data['total_score'] / data['total_marks']) * 100.0, 1)

        if pct >= 75:
            status = "Strong"
            badge_class = "badge-success"
        elif pct >= 60:
            status = "Moderate"
            badge_class = "badge-warning"
        else:
            status = "Needs Practice"
            badge_class = "badge-danger"

        result.append({
            'subject': subj,
            'attempts_count': data['attempts_count'],
            'total_score': data['total_score'],
            'total_marks': data['total_marks'],
            'percentage': pct,
            'status': status,
            'badge_class': badge_class,
        })

    # Sort descending by percentage
    result.sort(key=lambda x: x['percentage'], reverse=True)
    return result


def get_student_topic_performance(student: Student) -> List[Dict[str, Any]]:
    """
    CHECKPOINT 14: Calculates topic-wise aggregated performance for a student.
    """
    completed_attempts = Attempt.objects.filter(
        student=student,
        status='COMPLETED'
    ).select_related('assignment')

    topic_data: Dict[str, Dict[str, Any]] = {}

    for attempt in completed_attempts:
        topic = attempt.assignment.topic.strip() or "General Concepts"
        subject = attempt.assignment.subject.strip() or "General"
        key = f"{subject} - {topic}"
        if key not in topic_data:
            topic_data[key] = {
                'topic': topic,
                'subject': subject,
                'attempts_count': 0,
                'total_score': 0,
                'total_marks': 0,
            }
        topic_data[key]['attempts_count'] += 1
        topic_data[key]['total_score'] += attempt.score
        topic_data[key]['total_marks'] += attempt.assignment.total_marks

    result = []
    for key, data in topic_data.items():
        pct = 0.0
        if data['total_marks'] > 0:
            pct = round((data['total_score'] / data['total_marks']) * 100.0, 1)

        result.append({
            'topic': data['topic'],
            'subject': data['subject'],
            'attempts_count': data['attempts_count'],
            'total_score': data['total_score'],
            'total_marks': data['total_marks'],
            'percentage': pct,
            'is_weak': pct < 60.0
        })

    result.sort(key=lambda x: x['percentage'], reverse=True)
    return result


def get_final_exam_performance(student: Student) -> Dict[str, Any]:
    """
    CHECKPOINT 15: Isolates Final Exam performance from Subject-wise tests.
    """
    final_attempts = Attempt.objects.filter(
        student=student,
        status='COMPLETED',
        assignment__exam_type='FINAL'
    ).select_related('assignment')

    count = final_attempts.count()
    if count == 0:
        return {
            'attempted': False,
            'count': 0,
            'avg_percentage': 0.0,
            'total_score': 0,
            'total_marks': 0,
        }

    total_score = sum(a.score for a in final_attempts)
    total_marks = sum(a.assignment.total_marks for a in final_attempts)
    avg_pct = round((total_score / total_marks) * 100.0, 1) if total_marks > 0 else 0.0

    return {
        'attempted': True,
        'count': count,
        'avg_percentage': avg_pct,
        'total_score': total_score,
        'total_marks': total_marks,
    }


def calculate_placement_readiness(student: Student) -> Dict[str, Any]:
    """
    CHECKPOINT 16: Placement Readiness Score Calculation Algorithm.

    MATHEMATICAL FORMULA:
    Readiness Score = (Subject Performance × 0.40)
                    + (Final Exam Score × 0.25)
                    + (Profile Completion × 0.15)
                    + (CGPA Normalized × 0.10)
                    + (Completion / Consistency × 0.10)

    Components Explained:
    1. Subject Performance (40% weight):
       Average score on subject-specific tests (Data Structures, Python, etc.)
    2. Final Exam Score (25% weight):
       Performance on full-length mock placement tests.
       (If student has not taken a Final Exam yet, Subject Performance is used as a proxy
       to avoid unfairly penalizing new students while encouraging final exams).
    3. Profile Completion (15% weight):
       Percentage of profile completed (PRN, skills, projects, certifications).
    4. Academic CGPA (10% weight):
       Academic record normalized to a 100-point scale: (CGPA / 10.0) * 100.
    5. Test Completion Ratio (10% weight):
       Ratio of published assignments completed: (Completed / Total Available) * 100.

    Total bounds: Guaranteed between 0 and 100.
    """
    published_assignments = Assignment.objects.filter(status='PUBLISHED')
    total_published = published_assignments.count()

    completed_attempts = Attempt.objects.filter(
        student=student,
        status='COMPLETED'
    ).select_related('assignment')

    completed_count = completed_attempts.count()

    # 1. Subject Performance (40%)
    subject_attempts = completed_attempts.filter(assignment__exam_type='SUBJECT')
    if subject_attempts.exists():
        sub_score = sum(a.score for a in subject_attempts)
        sub_total = sum(a.assignment.total_marks for a in subject_attempts)
        subject_pct = (sub_score / sub_total * 100.0) if sub_total > 0 else 0.0
    else:
        # If student completed general attempts, use their overall completed percentage
        if completed_count > 0:
            c_score = sum(a.score for a in completed_attempts)
            c_total = sum(a.assignment.total_marks for a in completed_attempts)
            subject_pct = (c_score / c_total * 100.0) if c_total > 0 else 0.0
        else:
            subject_pct = 0.0

    # 2. Final Exam Performance (25%)
    final_exam_info = get_final_exam_performance(student)
    if final_exam_info['attempted']:
        final_pct = final_exam_info['avg_percentage']
    else:
        # Fallback to subject percentage if no final exam attempted yet
        final_pct = subject_pct * 0.7  # Slight incentive to take actual final exam

    # 3. Profile Completion (15%)
    profile_pct = float(student.profile_completion_percentage)

    # 4. Academic CGPA (10%)
    if student.cgpa and student.cgpa > 0:
        cgpa_pct = min(float(student.cgpa) * 10.0, 100.0)
    else:
        cgpa_pct = 0.0

    # 5. Completion / Consistency (10%)
    if total_published > 0:
        completion_ratio = min((completed_count / total_published) * 100.0, 100.0)
    else:
        completion_ratio = 100.0 if completed_count > 0 else 0.0

    # Weighted calculation
    readiness_raw = (
        (subject_pct * 0.40) +
        (final_pct * 0.25) +
        (profile_pct * 0.15) +
        (cgpa_pct * 0.10) +
        (completion_ratio * 0.10)
    )

    readiness_score = int(round(min(max(readiness_raw, 0.0), 100.0)))

    # Classification
    if readiness_score >= 80:
        band = "High Readiness"
        band_class = "band-high"
        summary_verdict = "Excellent! You are well prepared for placement technical interviews and drives."
    elif readiness_score >= 60:
        band = "Moderate Readiness"
        band_class = "band-moderate"
        summary_verdict = "Good foundational knowledge. Target your weak topics to achieve top placement readiness."
    else:
        band = "Needs Improvement"
        band_class = "band-low"
        summary_verdict = "Active preparation required. Complete available assignments and build your technical skills."

    return {
        'readiness_score': readiness_score,
        'band': band,
        'band_class': band_class,
        'summary_verdict': summary_verdict,
        'components': {
            'subject_pct': round(subject_pct, 1),
            'final_pct': round(final_pct, 1),
            'profile_pct': round(profile_pct, 1),
            'cgpa_pct': round(cgpa_pct, 1),
            'completion_ratio': round(completion_ratio, 1),
        },
        'completed_count': completed_count,
        'total_published': total_published,
    }


def get_all_student_rankings() -> List[Dict[str, Any]]:
    """
    CHECKPOINT 17: Global Student Ranking Algorithm.

    Sorts all students descending by Placement Readiness Score.
    Handles ties deterministically using:
    1. Readiness Score (descending)
    2. Final Exam Average (descending)
    3. Subject Performance (descending)
    4. Profile Completion (descending)
    5. Student ID (ascending)

    Returns ranked list of student dictionaries.
    """
    students = Student.objects.all()
    ranking_table = []

    for s in students:
        readiness_data = calculate_placement_readiness(s)
        final_info = get_final_exam_performance(s)

        ranking_table.append({
            'student_id': s.id,
            'name': s.name,
            'email': s.email,
            'department': s.department or "N/A",
            'year': s.year or "N/A",
            'cgpa': s.cgpa,
            'readiness_score': readiness_data['readiness_score'],
            'band': readiness_data['band'],
            'final_pct': final_info['avg_percentage'],
            'subject_pct': readiness_data['components']['subject_pct'],
            'profile_pct': readiness_data['components']['profile_pct'],
            'completed_count': readiness_data['completed_count'],
        })

    # Sort deterministically
    ranking_table.sort(
        key=lambda x: (
            -x['readiness_score'],
            -x['final_pct'],
            -x['subject_pct'],
            -x['profile_pct'],
            x['student_id']
        )
    )

    # Assign 1-indexed ranks
    for idx, row in enumerate(ranking_table, start=1):
        row['rank'] = idx

    return ranking_table


def get_student_rank(student: Student) -> Dict[str, Any]:
    """
    Retrieves the rank of a specific student and total student count.
    """
    rankings = get_all_student_rankings()
    total_students = len(rankings)

    for item in rankings:
        if item['student_id'] == student.id:
            return {
                'rank': item['rank'],
                'total_students': total_students,
                'percentile': round(((total_students - item['rank'] + 1) / total_students) * 100.0, 1) if total_students > 0 else 100.0,
            }

    return {'rank': 1, 'total_students': max(total_students, 1), 'percentile': 100.0}


def generate_improvement_plan(student: Student) -> Dict[str, Any]:
    """
    CHECKPOINT 18: Rule-Based Weak Area Detection & Improvement Plan.

    Analyzes student scores, detects weak subjects & topics (<60%),
    unattempted assignments, profile gaps, and generates a personalized
    actionable study roadmap for viva and placement drives.
    """
    readiness = calculate_placement_readiness(student)
    subject_perf = get_student_subject_performance(student)
    topic_perf = get_student_topic_performance(student)
    final_info = get_final_exam_performance(student)

    weak_subjects = [s for s in subject_perf if s['percentage'] < 60.0]
    strong_subjects = [s for s in subject_perf if s['percentage'] >= 75.0]
    weak_topics = [t for t in topic_perf if t['percentage'] < 60.0]

    # Find pending assignments
    completed_ids = Attempt.objects.filter(
        student=student,
        status='COMPLETED'
    ).values_list('assignment_id', flat=True)

    pending_assignments = Assignment.objects.filter(
        status='PUBLISHED'
    ).exclude(id__in=completed_ids)

    # Build action items list
    action_items = []

    # Priority 1: Weak Topics
    if weak_topics:
        for wt in weak_topics[:3]:
            action_items.append({
                'priority': 'HIGH',
                'category': 'Topic Revision',
                'title': f"Strengthen Topic: {wt['topic']} ({wt['subject']})",
                'description': f"Your current score in {wt['topic']} is {wt['percentage']}%. Review core theory, solve 15 practice MCQs, and re-attempt subject tests.",
                'badge': 'danger'
            })

    # Priority 2: Unattempted Final Exam
    if not final_info['attempted']:
        action_items.append({
            'priority': 'HIGH',
            'category': 'Mock Exam',
            'title': "Attempt Full-Length Placement Assessment",
            'description': "Taking full-length final exams contributes 25% to your readiness score and tests your exam endurance under timed constraints.",
            'badge': 'warning'
        })

    # Priority 3: Pending Subject Assignments
    if pending_assignments.exists():
        for pa in pending_assignments[:2]:
            action_items.append({
                'priority': 'MEDIUM',
                'category': 'Assignment',
                'title': f"Take Assignment: {pa.title}",
                'description': f"Subject: {pa.subject} | Time: {pa.time_limit} mins | Total Marks: {pa.total_marks}.",
                'badge': 'primary'
            })

    # Priority 4: Profile Gaps
    if student.profile_completion_percentage < 100:
        missing = []
        if not student.cgpa:
            missing.append("CGPA")
        if not student.skills:
            missing.append("Technical Skills")
        if not student.projects:
            missing.append("Projects")
        if not (student.resume_link or student.linkedin_url or student.github_url):
            missing.append("Professional Links")

        if missing:
            action_items.append({
                'priority': 'MEDIUM',
                'category': 'Profile Completion',
                'title': f"Complete Missing Profile Info: {', '.join(missing)}",
                'description': "A complete student profile demonstrates professionalism to placement recruiters and contributes 15% to your readiness score.",
                'badge': 'secondary'
            })

    # If student is doing great
    if not action_items:
        action_items.append({
            'priority': 'LOW',
            'category': 'Maintenance',
            'title': "Maintain Placement Consistency",
            'description': "All assignments completed with high accuracy! Continue revising core algorithmic patterns and competitive coding problems.",
            'badge': 'success'
        })

    return {
        'weak_subjects': weak_subjects,
        'strong_subjects': strong_subjects,
        'weak_topics': weak_topics,
        'pending_count': pending_assignments.count(),
        'action_items': action_items,
        'readiness': readiness,
    }
