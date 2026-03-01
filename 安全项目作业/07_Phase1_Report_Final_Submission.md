# ITP4103 Security Applications
## Phase 1 Report (Final Submission Draft)
### Preliminary Security Assessment of Intelligent Student Examination System

### 1. Executive Summary
This phase focuses on identifying practical security issues in a role-based online examination platform. The assessment covers authentication, authorization boundaries, API parameter handling, and critical business workflows.

Initial results indicate multiple vulnerabilities that may affect exam integrity, availability, and operational reliability. Findings are prioritized by likelihood and impact to support Phase 2 mitigation planning.

### 2. Testing Environment
- Runtime: Docker Compose
- Backend: Django API service
- Frontend: Vue client
- Database: MySQL
- Test identities: admin, teacher, student

### 3. Methodology
- OWASP-oriented checklist and scenario-driven testing
- Role-switch tests for horizontal/vertical privilege boundaries
- API validation for malformed and variant payloads
- Workflow tests for exam submit and score publication lifecycle

### 4. Test Coverage
| Category | Focus | Status |
|---|---|---|
| Authentication | login/session behavior | completed |
| Authorization | role boundary and operation access | completed |
| Input Validation | parameter and datetime handling | completed |
| Business Logic | exam submission and publication flow | completed |
| Configuration Baseline | runtime and endpoint behavior | completed |

### 5. Findings Summary
| ID | Finding | Severity | Impact |
|---|---|---|---|
| F-01 | Datetime format inconsistency causes exam creation failure | High | exam creation unavailable in affected flow |
| F-02 | API required-parameter mismatch in create-from-practice flow | High | request rejection and workflow interruption |
| F-03 | Answer persistence weakness during question switching | High | potential answer loss and fairness concern |
| F-04 | Submission timeout/instability under current processing path | High | failed submission perception and retry risk |
| F-05 | Status transition mismatch in publish lifecycle | Medium | teacher-side publish workflow blocked/misaligned |
| F-06 | Partial update safety issue in profile endpoint | Medium | data integrity risk under malformed update payloads |

### 6. Evidence and Reproducibility (Overview)
For each finding, the team prepared reproducible steps and artifacts including:
- API request/response records
- Error messages and runtime logs
- Interface behavior captures
- Before-fix state references

Detailed evidence is attached in appendix/screenshots package during final formatting.

### 7. Risk Prioritization
| Priority | Findings |
|---|---|
| P1 | F-01, F-02, F-03, F-04 |
| P2 | F-05, F-06 |

Remediation sequence in Phase 2 prioritizes P1 findings first due to direct impact on core examination operation.

### 8. Interim Conclusion
Phase 1 confirms that the most critical issues are concentrated in the exam workflow and API robustness. The next phase will implement targeted controls, align workflow status logic, and perform structured re-testing to demonstrate measurable improvements.
