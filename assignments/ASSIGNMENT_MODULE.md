# Placement Readiness Platform - Assignment Module Documentation

**Application Name:** `assignments`  
**Framework:** Django 6.1.1  
**Database:** MySQL (via PyMySQL)  
**Frontend:** Pure HTML5, Vanilla CSS3, Vanilla JavaScript (Zero External UI Libraries)  
**Authentication:** Custom Teaching Session-Based Authentication (Zero Django Auth Framework)

---

## 1. Executive Summary & Purpose

The **Assignment Module** is the core technical evaluation engine of the **Placement Readiness Platform**. Its primary objective is to evaluate a student's technical competence, conceptual clarity, and time management skills through standardized assessments.

The module provides:
1. **Hierarchical Categorization:** Distinguishes between **Final Exams** (comprehensive mock placement tests) and **Subject-wise Exams** (topic-level tests).
2. **Dual Question Paradigms:** Supports both **Single Choice (MCQ)** and **Multiple Select Questions (MSQ)**.
3. **Rigorous Evaluation:** Implements a strict **all-or-nothing** set comparison algorithm for MSQ questions to mirror real placement screening tests (e.g., GATE, TCS NQT, Infosys).
4. **Single-Attempt Enforcement:** Ensures examination integrity by strictly disallowing retakes through database constraints and view-layer checks.
5. **Real-Time Client & Server-Side Synchronized Timer:** Provides an intuitive countdown timer in Vanilla JavaScript with automatic form submission on timeout, backed by server-side elapsed-time validation.
6. **Detailed Post-Exam Solution Review:** Empowers student learning by displaying full question explanations, selected choices, and correct solutions immediately upon submission.

---

## 2. Technology Stack & Architectural Constraints

In accordance with college project rules, this entire module was built under strict constraints:
- **No External UI Frameworks:** No Bootstrap, Tailwind, React, Vue, or Angular.
- **No Third-Party Frontend Libraries:** No jQuery, Chart.js, or timer plugins.
- **No Django Built-in Auth for Business Logic:** Authentication relies on custom session management (`request.session['admin_id']` and `request.session['student_id']`) and our custom teaching-oriented password algorithm.
- **Relational Integrity:** Relies on pure MySQL tables with foreign keys and unique compound constraints.

---

## 3. Database Schema & Relational Design

The module consists of 6 normalized relational models in [`assignments/models.py`](models.py):

```
+--------------------+         +-------------------+         +------------------------+
|     Assignment     | 1 --- * |     Question      | 1 --- * |     QuestionOption     |
+--------------------+         +-------------------+         +------------------------+
| id (PK)            |         | id (PK)           |         | id (PK)                |
| title              |         | assignment_id(FK) |         | question_id (FK)       |
| exam_type          |         | question_text     |         | option_label (A,B,C,D) |
| subject            |         | question_type     |         | option_text            |
| topic              |         | marks             |         | is_correct (bool)      |
| time_limit (mins)  |         | solution (text)   |         +------------------------+
| total_marks        |         | order             |
| status             |         +-------------------+
| created_at         |
+--------------------+
          | 1
          |
          *
+--------------------+         +-------------------+         +------------------------+
|      Attempt       | 1 --- * |   StudentAnswer   | 1 --- * |  SelectedOptionRecord  |
+--------------------+         +-------------------+         +------------------------+
| id (PK)            |         | id (PK)           |         | id (PK)                |
| student_id (FK)    |         | attempt_id (FK)   |         | student_answer_id (FK) |
| assignment_id (FK) |         | question_id (FK)  |         | option_id (FK)         |
| started_at         |         | is_correct (bool) |         +------------------------+
| submitted_at       |         | marks_obtained    |
| score              |         +-------------------+
| percentage         |
| correct_count      |
| wrong_count        |
| unattempted_count  |
| status             |
| UNIQUE(student,    |
|        assignment) |
+--------------------+
```

### Table Specifications

#### 1. `assignments_assignment`
- **Purpose:** Stores test metadata and configuration.
- **Columns:**
  - `id`: `INT AUTO_INCREMENT PRIMARY KEY`
  - `title`: `VARCHAR(200)`
  - `exam_type`: `VARCHAR(20)` (`FINAL` or `SUBJECT`)
  - `subject`: `VARCHAR(100)` (e.g., Data Structures, Operating Systems, Aptitude)
  - `topic`: `VARCHAR(100)` (e.g., Arrays, Paging, Deadlocks)
  - `description`: `TEXT` (Instructions)
  - `time_limit`: `INT UNSIGNED` (Duration in minutes)
  - `total_marks`: `INT UNSIGNED` (Recalculated as sum of all question marks)
  - `status`: `VARCHAR(20)` (`DRAFT`, `PUBLISHED`, `CLOSED`)
  - `created_at`: `DATETIME`

#### 2. `assignments_question`
- **Purpose:** Stores individual problems linked to an assignment.
- **Columns:**
  - `id`: `INT AUTO_INCREMENT PRIMARY KEY`
  - `assignment_id`: `INT FOREIGN KEY REFERENCES assignments_assignment(id) ON DELETE CASCADE`
  - `question_text`: `TEXT`
  - `question_type`: `VARCHAR(10)` (`MCQ` or `MSQ`)
  - `marks`: `INT UNSIGNED` (e.g., 1, 2, 3, 5)
  - `solution`: `TEXT` (Step-by-step reasoning shown after submission)
  - `order`: `INT UNSIGNED`

#### 3. `assignments_questionoption`
- **Purpose:** Stores option choices for a question.
- **Columns:**
  - `id`: `INT AUTO_INCREMENT PRIMARY KEY`
  - `question_id`: `INT FOREIGN KEY REFERENCES assignments_question(id) ON DELETE CASCADE`
  - `option_label`: `VARCHAR(5)` (`A`, `B`, `C`, `D`)
  - `option_text`: `VARCHAR(500)`
  - `is_correct`: `BOOLEAN` (`True` if this option is part of the correct key)

#### 4. `assignments_attempt`
- **Purpose:** Tracks a student's session and scores for an assignment.
- **Columns:**
  - `id`: `INT AUTO_INCREMENT PRIMARY KEY`
  - `student_id`: `INT FOREIGN KEY REFERENCES student_student(id) ON DELETE CASCADE`
  - `assignment_id`: `INT FOREIGN KEY REFERENCES assignments_assignment(id) ON DELETE CASCADE`
  - `started_at`: `DATETIME`
  - `submitted_at`: `DATETIME NULL`
  - `score`: `INT UNSIGNED`
  - `percentage`: `FLOAT`
  - `correct_count`: `INT UNSIGNED`
  - `wrong_count`: `INT UNSIGNED`
  - `unattempted_count`: `INT UNSIGNED`
  - `status`: `VARCHAR(20)` (`IN_PROGRESS`, `COMPLETED`)
- **Constraint:** `UNIQUE KEY (student_id, assignment_id)`. This database-level constraint makes it physically impossible for a student to create two attempts for the same exam.

#### 5. `assignments_studentanswer`
- **Purpose:** Stores evaluation outcome per question for an attempt.
- **Columns:**
  - `id`: `INT AUTO_INCREMENT PRIMARY KEY`
  - `attempt_id`: `INT FOREIGN KEY REFERENCES assignments_attempt(id) ON DELETE CASCADE`
  - `question_id`: `INT FOREIGN KEY REFERENCES assignments_question(id) ON DELETE CASCADE`
  - `is_correct`: `BOOLEAN`
  - `marks_obtained`: `INT UNSIGNED`

#### 6. `assignments_selectedoptionrecord`
- **Purpose:** Stores exact options picked by the student (normalized 3NF structure).
- **Columns:**
  - `id`: `INT AUTO_INCREMENT PRIMARY KEY`
  - `student_answer_id`: `INT FOREIGN KEY REFERENCES assignments_studentanswer(id) ON DELETE CASCADE`
  - `option_id`: `INT FOREIGN KEY REFERENCES assignments_questionoption(id) ON DELETE CASCADE`

---

## 4. Admin Workflow & Capabilities

The Admin portal provides full lifecycle management:

```
[Create Assignment] (Status: DRAFT)
        ↓
[Author Questions] (MCQ/MSQ, Options A-D, Solution notes)
        ↓
[Publish Test] (Status: PUBLISHED → Now visible to students)
        ↓
[Monitor Submissions] (Class average, individual breakdown)
        ↓
[Close Test] (Status: CLOSED → Test archived)
```

1. **Assignment Creation ([`admin_assignment_create_view`](views_admin.py)):**
   - Admin defines Title, Category (`FINAL` or `SUBJECT`), Subject, Topic, Duration, and Description.
   - Assignment initializes in `DRAFT` status with `total_marks = 0`.
2. **Question Authoring ([`admin_assignment_questions_view`](views_admin.py)):**
   - Supports both `MCQ` and `MSQ`.
   - Admin provides options A, B, C, D and checks which options are correct.
   - For `MCQ`: Form enforces that exactly 1 option is marked correct.
   - For `MSQ`: Form allows multiple options to be marked correct.
   - Automatically calls `assignment.recalculate_total_marks()` upon each addition or deletion.
3. **Status Lifecycle ([`admin_assignment_status_toggle_view`](views_admin.py)):**
   - **`DRAFT`:** Visible only to Admin. Students cannot see or take it. Guard check: Cannot publish if questions count is 0.
   - **`PUBLISHED`:** Visible in the Student exam catalog. Students can start attempts.
   - **`CLOSED`:** Archived test. No further attempts permitted.
4. **Submissions Inspection ([`admin_assignment_submissions_view`](views_admin.py)):**
   - Displays all students who took the test.
   - Shows Class Average Score, Average Percentage, and each student's `Correct / Wrong / Unattempted` breakdown.

---

## 5. Student Workflow & Test Taking Engine

```
[Student Catalog] (Only status='PUBLISHED')
        ↓
[Start Test] (Checks single-attempt rule & creates Attempt: IN_PROGRESS)
        ↓
[Test Workspace] (Sticky Countdown Timer + Question Palette)
        ↓ (Auto-submit on timeout OR manual submit)
[Scoring Engine] (All-or-Nothing MSQ & MCQ evaluation)
        ↓
[Result & Review] (Score Card + Detailed Solutions)
```

1. **Catalog & Filtering ([`student_assignment_list_view`](views_student.py)):**
   - Students filter tests by "All", "Final Exam", or "Subject-wise Exam".
   - Each card displays Duration, Question count, Max marks, and Status:
     - `Not Attempted` -> Displays **Start Test** button.
     - `Completed` -> Displays **View Result** button with their score.
2. **Single-Attempt Guard ([`student_start_attempt_view`](views_student.py)):**
   - If the student has already completed the test, the system immediately redirects them to their Result screen with an informative message.
3. **Examination Interface ([`student_attempt_view`](views_student.py)):**
   - Clean, distraction-free environment.
   - Distinct input controls: Radio buttons for MCQ; Checkboxes with "(Select all that apply)" for MSQ.
   - Interactive question palette on the right side: buttons show answered (blue) vs unanswered (gray) in real-time, and clicking any number jumps to that question.
4. **Post-Exam Solutions ([`student_result_view`](views_student.py)):**
   - Shows score, percentage rating, and time elapsed.
   - Visual color coding:
     - Green badge: "✓ Correct Answer"
     - Blue badge: "Your Choice"
     - Red badge: "Wrong Pick"
   - Full explanation and solution displayed for each question.

---

## 6. The Mathematical Scoring Engine

The core evaluation logic resides in [`assignments/logic/scoring.py`](logic/scoring.py).

### Formal Evaluation Rules

Let $Q$ be the set of questions in the assignment.  
For each question $q \in Q$:
- Let $C_q = \{ \text{id of option } o \mid o \in q.\text{options} \land o.\text{is\_correct} = \text{True} \}$
- Let $S_q = \{ \text{id of option } o \mid \text{submitted by student for } q \}$
- Let $M_q$ be the maximum marks allotted for question $q$.

#### 1. Unattempted Condition:
$$\text{If } S_q = \emptyset \implies \text{Marks}_q = 0, \quad \text{UnattemptedCount} \mathrel{+}= 1$$

#### 2. Single Choice (MCQ) Evaluation:
$$|C_q| = 1 \implies \text{Marks}_q = \begin{cases} M_q & \text{if } S_q = C_q \\ 0 & \text{if } S_q \neq C_q \end{cases}$$

#### 3. Multiple Select (MSQ) Strict All-or-Nothing Evaluation:
$$|C_q| \ge 1 \implies \text{Marks}_q = \begin{cases} M_q & \text{if } S_q = C_q \\ 0 & \text{if } S_q \neq C_q \end{cases}$$

> **Why Strict All-or-Nothing?**  
> In standardized engineering placement tests (such as GATE, TCS NQT, and AMCAT), MSQ questions do not award partial marks. If the correct set is $\{B, D\}$:
> - Student selects $\{B, D\} \implies$ Full Marks ($M_q$).
> - Student selects $\{B\} \implies$ **0 Marks** (Missed $D$).
> - Student selects $\{B, D, C\} \implies$ **0 Marks** (Selected incorrect $C$).

#### 4. Aggregate Metrics:
$$\text{Total Score} = \sum_{q \in Q} \text{Marks}_q$$
$$\text{Percentage} = \left( \frac{\text{Total Score}}{\sum_{q \in Q} M_q} \right) \times 100$$

All writes to `assignments_attempt`, `assignments_studentanswer`, and `assignments_selectedoptionrecord` are wrapped inside a Django `transaction.atomic()` block, guaranteeing complete database ACID consistency.

---

## 7. Timer Synchronization Architecture

```
[Server: Started_at] ────> [Client: remaining_seconds]
                                   │
                                   ▼
                       [Vanilla JS 1s Interval]
                                   │
                    ┌──────────────┴──────────────┐
                    ▼                             ▼
           [Time > 0: Tick]            [Time = 0: Timeout]
                                                  │
                                                  ▼
                                      [Auto-submit Form (POST)]
                                                  │
                                                  ▼
                                     [Server: Elapsed Check]
```

1. **Server-Side Computation:**
   $$\text{elapsed\_seconds} = \text{now}() - \text{attempt.started\_at}$$
   $$\text{remaining\_seconds} = \max(0, (\text{time\_limit} \times 60) - \text{elapsed\_seconds})$$
2. **Client-Side Countdown ([`assignments/static/assignments/js/timer.js`](static/assignments/js/timer.js)):**
   - Reads `data-remaining-seconds` from `#timerDisplay`.
   - Runs a 1-second interval loop updating `MM:SS`.
   - When $\le 120$ seconds remain, adds `.timer-warning` (red pulsing effect).
   - When timer hits `00:00`, clears interval, alerts student, and invokes `testForm.submit()`.
3. **Latency Grace Period:**
   - Server validates submitted attempts with a 15-second grace window to absorb realistic network latency while preventing client-side clock manipulation.

---

## 8. Viva & Project Defense Guide (15 Key Questions)

Here are the most common questions college professors and project examiners ask, along with the exact technical answers:

### Q1: What makes your Assignment Module different from standard online quiz templates?
**Answer:**  
"Our module is built specifically for campus placement readiness. It implements a two-tier hierarchy (`Final Exam` vs `Subject-wise Exam`), dual question formats (`MCQ` and `MSQ`), a mathematical all-or-nothing set-based scoring engine, database-enforced single attempts, and server-client synchronized countdown timers without relying on any external UI frameworks or third-party libraries."

### Q2: Why did you implement strict All-or-Nothing scoring for MSQs instead of partial marks?
**Answer:**  
"In technical placement examinations (such as GATE and top tech firm screening rounds), multiple-choice questions test comprehensive understanding. Awarding partial marks encourages guesswork. Set equality ($S_q = C_q$) guarantees that candidates receive credit only when they demonstrate mastery by identifying all correct options without selecting any wrong distractors."

### Q3: How do you prevent a student from attempting an assignment multiple times?
**Answer:**  
"We protect against retakes at two separate layers:
1. **Database Layer:** The `Attempt` model defines `unique_together = ('student', 'assignment')`. MySQL creates a unique compound index on `(student_id, assignment_id)`. Any attempt to insert a duplicate record triggers an `IntegrityError`.
2. **Application / View Layer:** `student_start_attempt_view` checks if an attempt exists with `status='COMPLETED'`. If so, it immediately redirects the student to their Result page."

### Q4: How is the countdown timer prevented from being bypassed if the student refreshes the browser?
**Answer:**  
"The timer is not stored purely in client-side memory. When the student clicks 'Start Test', the server records `started_at` in MySQL. When the page is loaded or refreshed, the server computes `remaining_seconds = (time_limit * 60) - (timezone.now() - started_at)`. Even if the student reloads the page or changes browser tabs, the elapsed time continues to count down accurately."

### Q5: How do you prevent students from seeing Draft assignments?
**Answer:**  
"In `student_assignment_list_view`, the ORM query strictly filters:
`Assignment.objects.filter(status='PUBLISHED')`
Drafts (`status='DRAFT'`) and closed exams (`status='CLOSED'`) are completely excluded from student queries at the database level."

### Q6: Why did you not use Django's built-in `auth.User` model for the students and admins?
**Answer:**  
"Our project requirement is educational transparency. By building our own lightweight `Student` and `Admin` models and custom session management, we demonstrate full control over data flow, session lifecycle (`request.session.cycle_key()`, `flush()`), and our custom teaching-oriented password algorithm without framework magic."

### Q7: What happens if a student loses internet connection during the test?
**Answer:**  
"Because the student's attempt is marked `IN_PROGRESS` in MySQL, if the student reconnects within the time limit, visiting the assignment URL resumes their test with the exact remaining time calculated against the original `started_at` timestamp."

### Q8: How is database consistency guaranteed during test submission?
**Answer:**  
"In [`assignments/logic/scoring.py`](logic/scoring.py), the entire evaluation loop—deleting any draft answers, inserting `StudentAnswer` records, inserting `SelectedOptionRecord` rows, and updating `Attempt` status to `COMPLETED`—is enclosed in `with transaction.atomic():`. If any database operation fails, the transaction is rolled back, preventing orphaned or corrupted records."

### Q9: What is the purpose of the `SelectedOptionRecord` table?
**Answer:**  
"To maintain Third Normal Form (3NF). Because an MSQ question allows a student to choose multiple options ($1 \le k \le 4$), storing option IDs as comma-separated strings inside `StudentAnswer` would violate 1NF and make SQL queries inefficient. `SelectedOptionRecord` models a clean one-to-many relationship (`StudentAnswer` 1 $\rightarrow$ * `SelectedOptionRecord`)."

### Q10: How does the Admin know the overall difficulty or class performance on an exam?
**Answer:**  
"In [`admin_assignment_submissions_view`](views_admin.py), the backend executes SQL aggregate queries: `Attempt.objects.filter(assignment=assignment, status='COMPLETED').aggregate(Avg('score'), Avg('percentage'))`. The admin dashboard displays the Class Average Score, Average Percentage, and total completion count."

### Q11: How are questions sequenced?
**Answer:**  
"Every `Question` record has an `order` integer field. When an admin deletes a question, `admin_question_delete_view` automatically re-sequences the remaining questions ($1, 2, 3 \dots$) to ensure that students always see an uninterrupted sequence."

### Q12: How are Total Marks computed for an assignment?
**Answer:**  
"Total marks are not manually guessed. When questions are added or removed, `assignment.recalculate_total_marks()` runs `self.questions.aggregate(models.Sum('marks'))` and updates `assignment.total_marks` in MySQL."

### Q13: Can an Admin publish an assignment with no questions?
**Answer:**  
"No. Both `admin_assignment_status_toggle_view` and `admin_assignment_questions_view` include validation that checks `if assignment.questions.count() == 0:`. If so, publishing is blocked with an error message informing the admin to add at least one question."

### Q14: How does the Question Palette in the examination interface work?
**Answer:**  
"The palette is implemented in Vanilla JS in [`timer.js`](static/assignments/js/timer.js). It attaches an `onchange` listener to all radio buttons and checkboxes. When an input is checked, it marks the corresponding question card as answered and applies the `.answered` class to the palette button. Clicking any palette button executes `element.scrollIntoView({ behavior: 'smooth', block: 'center' })`."

### Q15: What security measures prevent one student from viewing another student's test results?
**Answer:**  
"In `student_result_view`, the ORM query filters strictly by the authenticated student's session:
`Attempt.objects.filter(student=request.student, assignment=assignment, status='COMPLETED')`.
A student cannot view another student's submission simply by altering the URL parameters."

---

## 9. File Structure Summary

```
D:\Basic_Lad\assignments\
├── logic\
│   ├── __init__.py
│   ├── scoring.py          # All-or-nothing MSQ & MCQ evaluation engine
│   └── security.py         # Session decorators (admin_required, student_required)
├── migrations\
│   ├── 0001_initial.py     # Initial MySQL migration for 6 models
│   └── __init__.py
├── static\
│   └── assignments\
│       ├── css\
│       │   └── assignments.css # Professional vanilla responsive styling
│       └── js\
│           └── timer.js        # Countdown timer & palette interactivity
├── templates\
│   └── assignments\
│       ├── admin\
│       │   ├── list.html        # Admin assignment catalog with filters
│       │   ├── create.html      # Create assignment form
│       │   ├── edit.html        # Edit metadata form
│       │   ├── questions.html   # Question authoring (MCQ/MSQ options & solutions)
│       │   └── submissions.html # Class score analysis & submissions
│       └── student\
│           ├── list.html        # Student exam catalog
│           ├── attempt.html     # Test taking workspace with timer
│           ├── result.html      # Performance card & detailed solutions
│           └── results_list.html# Student's past test history
├── admin.py
├── apps.py                 # AppConfig for 'assignments'
├── models.py               # 6 normalized relational MySQL models
├── urls.py                 # Admin & Student URL route mappings
├── views_admin.py          # Admin management views
├── views_student.py        # Student testing & review views
└── ASSIGNMENT_MODULE.md    # Comprehensive technical & viva documentation
```
