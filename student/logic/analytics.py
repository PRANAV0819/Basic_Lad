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
from django.db.models import Q
from student.models import Student
from assignments.models import Assignment, Attempt


SUBJECT_SHORT_NAMES = {
    'Percentages, Ratios and Proportions': 'Quant',
    'Time, Speed and Distance': 'TSD',
    'Time and Work': 'Time & Work',
    'Probability and Permutations': 'Prob & PnC',
    'Number Systems': 'Numbers',
    'Number and Letter Series': 'Series',
    'Direction Sense': 'Direction',
    'Syllogisms': 'Syllogisms',
    'Blood Relations': 'Blood Rel',
    'Seating Arrangements': 'Seating',
    'Coding-Decoding': 'Coding',
    'Data Structures': 'DS',
    'Data Structures and Algorithms (DSA)': 'DSA',
    'Arrays & Strings': 'Arrays',
    'Stacks & Queues': 'Stacks',
    'Linked Lists': 'Lists',
    'Trees & Graphs': 'Trees',
    'Searching & Sorting': 'Search/Sort',
    'Recursion and Dynamic Programming': 'Recursion',
    'Database Management Systems (DBMS)': 'DBMS',
    'Operating Systems (OS)': 'OS',
    'Computer Networks and Cloud Computing (CN&CC)': 'Networks',
    'Object-Oriented Programming (OOP)': 'OOPs',
    'Core Computer Science': 'Core CS',
    'Programming Fundamentals - C/C++ or Python': 'Prog Fund',
    'Verbal Communication': 'Verbal',
}


def get_subject_short_name(subject_name: str) -> str:
    """Returns a clean concise abbreviation/short-form of a subject name for chart display."""
    if not subject_name:
        return ""
    clean = subject_name.strip()
    if clean in SUBJECT_SHORT_NAMES:
        return SUBJECT_SHORT_NAMES[clean]
    for full, short in SUBJECT_SHORT_NAMES.items():
        if full.lower() in clean.lower():
            return short
    if len(clean) > 10:
        words = clean.split()
        if len(words) > 1:
            return "".join(w[0].upper() for w in words if w.isalnum())[:8]
        return clean[:10]
    return clean


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
        status__in=['COMPLETED', 'SUBMITTED', 'AUTO_SUBMITTED']
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
            'short_name': get_subject_short_name(subj),
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
        status__in=['COMPLETED', 'SUBMITTED', 'AUTO_SUBMITTED']
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
        status__in=['COMPLETED', 'SUBMITTED', 'AUTO_SUBMITTED'],
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

    MATHEMATICAL FORMULA (Updated Placement Readiness Weightage):
    Readiness Score = (Coding & DSA × 0.25)
                    + (Core CS Subjects × 0.25)
                    + (Aptitude × 0.15)
                    + (Logical Reasoning × 0.15)
                    + (Academic CGPA Normalized × 0.10)
                    + (Communication Skills × 0.10)

    Components Explained:
    1. Coding & DSA (25% weight):
       Performance in Programming fundamentals, Data Structures, Algorithms, Recursion & Dynamic Programming.
    2. Core CS Subjects (25% weight):
       Performance in foundational computer science: OOP, DBMS, Operating Systems, Computer Networks.
    3. Aptitude (15% weight):
       Quantitative aptitude, Percentages, Profit & Loss, Time & Work, Speed & Distance, Number Systems.
    4. Logical Reasoning (15% weight):
       Analytical puzzles, Series, Coding-Decoding, Seating Arrangements, Blood Relations, Syllogisms.
    5. Academic CGPA (10% weight):
       Academic record normalized to a 100-point scale: (CGPA / 10.0) * 100.
    6. Communication Skills (10% weight):
       Verbal communication, corporate English fluency, grammar, comprehension, and interview readiness.

    Total bounds: Strictly bounded between 0 and 100.
    """
    published_assignments = Assignment.objects.filter(status='PUBLISHED')
    total_published = published_assignments.count()

    completed_attempts = Attempt.objects.filter(
        student=student,
        status__in=['COMPLETED', 'SUBMITTED', 'AUTO_SUBMITTED']
    ).select_related('assignment', 'assignment__module')

    completed_count = completed_attempts.count()

    # Helper: calculate module-specific score percentage strictly from actual attempts
    def get_module_percentage(module_codes, subject_keywords=None):
        if not isinstance(module_codes, (list, tuple, set)):
            module_codes = [module_codes]

        # 1. Primary: Match strictly by module assignment
        attempts = completed_attempts.filter(assignment__module__code__in=module_codes)

        # 2. Secondary fallback: ONLY for legacy assignments where module foreign key is NULL
        if not attempts.exists() and subject_keywords:
            q_filter = Q()
            for kw in subject_keywords:
                q_filter |= Q(assignment__subject__icontains=kw)
            attempts = completed_attempts.filter(q_filter, assignment__module__isnull=True)

        if attempts.exists():
            score = sum(a.score for a in attempts)
            total = sum(a.assignment.total_marks for a in attempts)
            return (score / total * 100.0) if total > 0 else 0.0
        return 0.0

    # 1. Coding & DSA (25% weight) - strictly 0.0% if unattempted
    coding_dsa_pct = get_module_percentage(
        ['CODING_DSA'],
        ['Coding', 'DSA', 'Algorithm', 'Data Structure', 'Program', 'Tree', 'Graph']
    )

    # 2. Core CS Subjects (25% weight) - strictly 0.0% if unattempted
    core_subjects_pct = get_module_percentage(
        ['CORE_SUBJECTS'],
        ['Core', 'DBMS', 'Operating System', 'OS', 'Network', 'OOP', 'Database']
    )

    # 3. Aptitude (15% weight) - strictly 0.0% if unattempted
    aptitude_pct = get_module_percentage(
        ['APTITUDE'],
        ['Aptitude', 'Quantitative', 'Math', 'Percentage', 'Profit', 'Work']
    )

    # 4. Logical Reasoning (15% weight) - strictly 0.0% if unattempted
    logical_reasoning_pct = get_module_percentage(
        ['LOGICAL_REASONING'],
        ['Reasoning', 'Logical', 'Puzzle', 'Series', 'Relation', 'Syllogism', 'Direction']
    )

    # 5. Academic CGPA (10% weight) - normalized from degree CGPA
    if student.cgpa and student.cgpa > 0:
        cgpa_pct = min(float(student.cgpa) * 10.0, 100.0)
    else:
        cgpa_pct = 0.0

    # 6. Communication Skills (10% weight) - strictly 0.0% if unattempted
    communication_pct = get_module_percentage(
        ['COMMUNICATION_SKILLS', 'COMMUNICATION'],
        ['Communication', 'Verbal', 'English', 'Interview', 'Grammar', 'Corporate', 'Vocabulary']
    )

    # Legacy profile metric tracking
    profile_ratio = float(student.profile_completion_percentage)
    if total_published > 0:
        test_ratio = min((completed_count / total_published) * 100.0, 100.0)
    else:
        test_ratio = 100.0 if completed_count > 0 else 0.0

    # Weighted calculation
    readiness_raw = (
        (coding_dsa_pct * 0.25) +
        (core_subjects_pct * 0.25) +
        (aptitude_pct * 0.15) +
        (logical_reasoning_pct * 0.15) +
        (cgpa_pct * 0.10) +
        (communication_pct * 0.10)
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
            'coding_dsa_pct': round(coding_dsa_pct, 1),
            'core_subjects_pct': round(core_subjects_pct, 1),
            'aptitude_pct': round(aptitude_pct, 1),
            'logical_reasoning_pct': round(logical_reasoning_pct, 1),
            'cgpa_pct': round(cgpa_pct, 1),
            'communication_pct': round(communication_pct, 1),
            # Backwards compatibility keys
            'profile_consistency_pct': round(communication_pct, 1),
            'subject_pct': round(core_subjects_pct, 1),
            'final_pct': round(coding_dsa_pct, 1),
            'profile_pct': round(profile_ratio, 1),
            'completion_ratio': round(test_ratio, 1),
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
        status__in=['SUBMITTED', 'AUTO_SUBMITTED', 'COMPLETED']
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
