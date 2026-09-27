# PLACEMENT READINESS PLATFORM — COMPLETE TECHNICAL SPECIFICATION & VIVA GUIDE

## 1. Project Purpose & System Overview

The **Placement Readiness Platform** is a college web application designed to help engineering and computer science students evaluate, track, and improve their technical and academic readiness for campus recruitment drives.

### System Architecture
- **Web Framework:** Python Django (MVT Architecture)
- **Database:** MySQL relational database (`placement_readiness`) via PyMySQL
- **Frontend:** Vanilla HTML5, Modern Responsive CSS3, Vanilla JavaScript (No React, Bootstrap, Tailwind, or jQuery)
- **Authentication:** Custom Session-based authentication with custom mathematical password hashing (Zero Django Auth dependency)
- **User Roles:** Exactly Two Roles — **Student** and **Administrator**

---

## 2. Relational Database Schema (MySQL)

```text
+-------------------+       1:N       +---------------------+
|  student_student  |---------------->| assignments_attempt |
+-------------------+                 +---------------------+
| id (PK)           |                    | id (PK)           |
| name              |                    | student_id (FK)   |
| email (UNIQUE)    |                    | assignment_id(FK) |
| password_hash(64) |                    | score             |
| salt (64)         |                    | percentage        |
| prn               |                    | correct_count     |
| cgpa              |                    | wrong_count       |
| department        |                    | unattempted_count |
| year              |                    | status            |
| skills (Text)     |                    | started_at        |
| projects (Text)   |                    | submitted_at      |
| certifications    |                    +---------------------+
| resume_link       |                               |
| linkedin_url      |                               | 1:N
| github_url        |                               v
+-------------------+                 +---------------------------+
                                      | assignments_studentanswer |
+------------------------+            +---------------------------+
| assignments_assignment |            | id (PK)                   |
+------------------------+            | attempt_id (FK)           |
| id (PK)                |            | question_id (FK)          |
| title                  |            | is_correct (Bool)         |
| exam_type (FINAL/SUBJ) |            | marks_obtained            |
| subject                |            +---------------------------+
| topic                  |                          |
| time_limit (mins)      |                          | 1:N
| total_marks            |                          v
| status (DRAFT/PUB/CLO) |            +----------------------------------+
+------------------------+            | assignments_selectedoptionrecord |
           |                          +----------------------------------+
           | 1:N                      | id (PK)                          |
           v                          | student_answer_id (FK)           |
+----------------------+              | option_id (FK)                   |
| assignments_question |              +----------------------------------+
+----------------------+
| id (PK)              |
| assignment_id (FK)   |
| question_text        |
| question_type(MCQ/MSQ|
| marks                |
| solution_text        |
+----------------------+
           |
           | 1:N
           v
+----------------------------+
| assignments_questionoption |
+----------------------------+
| id (PK)                    |
| question_id (FK)           |
| option_label (A/B/C/D)     |
| option_text                |
| is_correct (Boolean)       |
+----------------------------+
```

---

## 3. Custom Teaching Password Algorithm

### Why Custom Hashing?
College project guidelines mandate manual logic demonstration. Rather than relying on ready-made black-box libraries (`bcrypt`, `make_password`), we wrote an explicit, explainable cryptographic hashing module.

### Mathematical Mechanism:
1. **Salt Generation:** `secrets.token_hex(32)` produces a cryptographically secure 64-character hexadecimal salt.
2. **Combination:** Plaintext password and per-user salt are concatenated: `combined = password + salt`.
3. **State Constants:** Four 32-bit registers initialized with seeds:
   `values = [2166136261, 16777619, 2246822519, 3266489917]`
4. **FNV Prime Mixing:**
   For each character `c` at `index`:
   - `code = ord(c)`
   - `slot = index % 4`
   - `values[slot] = ((values[slot] ^ code) * 16777619) % (2^32)`
5. **Digest Formatting:** The 4 integers are converted to 8-character hex strings, multiplied and sliced to exactly 64 hexadecimal characters.

---

## 4. MCQ vs MSQ Scoring Engine

Located in [assignments/logic/scoring.py](file:///D:/Basic_Lad/assignments/logic/scoring.py).

### Mathematical Rules:
- **MCQ (Single Choice):** Exactly one option selected. Full marks if `selected == correct`, else 0.
- **MSQ (Multiple Select Question):** **STRICT ALL-OR-NOTHING MARKING**.
  - Let $C$ be the set of correct option IDs for question $Q$.
  - Let $S$ be the set of option IDs selected by the student.
  - Marks awarded:
    $$M = \begin{cases} \text{marks}(Q) & \text{if } S = C \\ 0 & \text{if } S \neq C \end{cases}$$
  - **Zero partial credit:** If $C = \{A, B, C\}$ and student selects $\{A, B\}$, $S \neq C \implies M = 0$.
  - **Penalty for over-selection:** If student selects $\{A, B, C, D\}$, $S \neq C \implies M = 0$.

---

## 5. Placement Readiness Score Algorithm

Located in [student/logic/analytics.py](file:///D:/Basic_Lad/student/logic/analytics.py).

### Mathematical Weightage Breakdown (Guaranteed 0 - 100):

$$\text{Readiness Score} = (S \times 0.40) + (F \times 0.25) + (P \times 0.15) + (C \times 0.10) + (R \times 0.10)$$

| Component | Weight | Calculation Method | Description |
|-----------|--------|--------------------|-------------|
| **Subject Performance ($S$)** | **40%** | $\frac{\sum \text{Score}_{\text{subj}}}{\sum \text{Total}_{\text{subj}}} \times 100$ | Aggregate percentage across subject tests (Data Structures, Python, DBMS, etc.) |
| **Final Exam Score ($F$)** | **25%** | $\frac{\sum \text{Score}_{\text{final}}}{\sum \text{Total}_{\text{final}}} \times 100$ | Average on full-length mock placement assessments |
| **Profile Completion ($P$)** | **15%** | 10 key profile fields $\times$ 10% each | Academic, technical, and project portfolio completeness |
| **Normalized CGPA ($C$)** | **10%** | $\min\left(\frac{\text{CGPA}}{10.0} \times 100, 100\right)$ | Academic consistency from college degree |
| **Completion Ratio ($R$)** | **10%** | $\frac{\text{Completed Tests}}{\text{Total Available Tests}} \times 100$ | Test discipline and continuous engagement |

### Readiness Bands:
- **High Readiness ($\ge 80\%$):** Ready for product company placement interviews.
- **Moderate Readiness ($60\% - 79\%$):** Solid foundation; targeted practice needed.
- **Needs Improvement ($< 60\%$):** Requires foundational revision and more test practice.

---

## 6. Student Ranking & Tie-Breaking Rules

Students are ranked globally on the college leaderboard using deterministic sorting:
1. **Primary Sort:** Placement Readiness Score (Descending)
2. **Tie-Breaker 1:** Final Exam Score (Descending)
3. **Tie-Breaker 2:** Subject Performance Score (Descending)
4. **Tie-Breaker 3:** Profile Completion Percentage (Descending)
5. **Tie-Breaker 4:** Student Database ID (Ascending)

---

## 7. Rule-Based Improvement Plan (Weak Area Detection)

1. **Weak Topic & Subject Detection:** Identifies any topic or subject where student accuracy is $< 60\%$.
2. **Missing Exam Alerts:** Flags unattempted Final Mock Placement Assessments.
3. **Pending Tests:** Recommends published assignments not yet attempted.
4. **Portfolio Gaps:** Pinpoints missing fields (CGPA, resume link, GitHub profile, technical skills).
5. **Actionable Roadmap:** Each recommendation has an assigned priority level (`HIGH`, `MEDIUM`, `LOW`) and specific study guidance.

---

## 8. College Viva Preparation Questions & Answers

### Q1: Why did you not use Django's built-in User and auth system?
**Answer:** Django's built-in authentication uses PBKDF2/bcrypt hashing, pre-configured permission tables, and standard User models that abstract the security mechanics away. For our college project, we implemented our own custom database schema (`Student` and `Admin`), random salt generator (`secrets.token_hex(32)`), FNV-modulo hash algorithm, and session management (`request.session`) to prove our understanding of web security fundamentals.

### Q2: How does your password hashing prevent rainbow table attacks?
**Answer:** A rainbow table is a precomputed table of plaintext passwords and their corresponding hashes. Because we generate an unpredictable 64-character random salt per user and combine it with the password before hashing, even if two students use the exact same password (e.g. `password123`), their resulting stored hashes will be completely different. A precomputed table cannot be used without knowing each unique salt.

### Q3: How do you enforce that a student cannot re-attempt an assignment?
**Answer:** We enforce this at two layers:
1. **Database Layer:** The `assignments_attempt` table has a `unique_together = ('student', 'assignment')` database constraint. MySQL will physically reject any duplicate attempt insert.
2. **Application Layer:** In [assignments/views_student.py](file:///D:/Basic_Lad/assignments/views_student.py), before starting or submitting an attempt, we query `Attempt.objects.filter(student=student, assignment=assignment).exists()`. If true, the student is redirected to their solution review page.

### Q4: Explain the MSQ evaluation algorithm.
**Answer:** In Multiple Select Questions, more than one option can be correct. We convert the submitted option IDs into a Python set `selected_ids` and the database correct option IDs into `correct_ids`. We evaluate using mathematical set equality: `if selected_ids == correct_ids: marks = question.marks else: marks = 0`. This strictly guarantees all-or-nothing scoring.

### Q5: How is session security handled without external auth libraries?
**Answer:** When an admin or student logs in successfully:
1. The server sets session keys: `request.session['is_student_logged_in'] = True` and `request.session['student_id'] = student.id`.
2. We call `request.session.cycle_key()` to prevent Session Fixation attacks.
3. On logout, we execute `request.session.flush()`, which purges the session data from both the server-side database and the client's cookie.
4. Custom decorators (`@admin_required`, `@student_required`) verify this server-side state before permitting view execution.

### Q6: What happens if a student tampers with the countdown timer in their browser?
**Answer:** The frontend JavaScript countdown timer is purely for student user experience. The definitive remaining time is verified and enforced on the server. When the attempt is initiated, `started_at` is timestamped in MySQL. On submission, the server computes the elapsed time against `assignment.time_limit`. Client-side clock manipulation cannot bypass server evaluation.
