# ITP4103 Security Applications
## Presentation Script (Final Submission Draft, 8–10 minutes)

### Slide 1: Title and Team (30s)
Good morning/afternoon. We are presenting the security assessment project for our Intelligent Student Examination System. This presentation covers vulnerabilities identified, mitigation measures, implementation evidence, and re-test outcomes.

### Slide 2: Project and Architecture Overview (45s)
Our system uses a Vue frontend, Django backend, and MySQL database, deployed with Docker Compose. It supports admin, teacher, and student workflows, including exam creation, answer submission, score publication, and AI-assisted functions.

### Slide 3: Scope and Methodology (60s)
Our assessment scope includes authentication, authorization, API input validation, exam business logic, and runtime configuration baseline. We referenced OWASP guidance and used a combination of manual testing, API tampering, and regression verification.

### Slide 4: Key Finding 1 (60s)
We identified exam creation failures caused by datetime format inconsistency and parameter mismatch. The impact was direct workflow interruption when creating exams from practice papers.

### Slide 5: Key Finding 2 (60s)
We found answer persistence and submission reliability issues. Under certain navigation and timing conditions, users could experience answer loss perception or submission timeout behavior.

### Slide 6: Key Finding 3 (60s)
We identified lifecycle status mismatch between student submission and teacher score publication, causing operational inconsistency in the publish process.

### Slide 7: Mitigation and Implementation (90s)
We implemented backend normalization and compatibility handling, frontend persistence safeguards, submission flow protection, and lifecycle status correction. We also hardened partial profile updates for better data integrity.

### Slide 8: Re-test and Validation (60s)
Post-fix verification shows full feature smoke tests passed 25 out of 25. Focused exam workflow regression tests passed 3 out of 3. Runtime services remained healthy after container restart verification.

### Slide 9: Value and Bonus Implementation (45s)
The project demonstrates practical security improvement from finding to implementation and verification. This satisfies the requirement of relevant testing, practical mitigation recommendation, and actual implementation.

### Slide 10: Conclusion and Q&A (30s)
In conclusion, we established an end-to-end security improvement loop with measurable outcomes. Thank you. We are ready for questions.
