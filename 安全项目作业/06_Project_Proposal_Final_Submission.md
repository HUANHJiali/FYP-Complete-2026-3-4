# ITP4103 Security Applications
## Project Proposal (Final Submission Draft)

### 1. Project Information
- Programme: HD in Cloud and Data Centre Administration
- Module: ITP4103 Security Applications
- Project Base: Final Year Project (Intelligent Student Examination System)
- Team Size: 3–5 members

### 2. Background and Motivation
The proposed project is a web-based intelligent examination platform designed for administrators, teachers, and students. It supports exam management, practice papers, task assignment, AI-assisted scoring, and AI question generation.

As the platform handles sensitive educational records, role-based operations, and assessment results, security risks directly impact data integrity, service availability, and fairness of examination workflows. Therefore, a structured security assessment and mitigation plan is necessary.

### 3. System Architecture (Brief)
- Frontend: Vue 3 + View UI Plus
- Backend: Django 4.1.3 (API-based services)
- Database: MySQL 8.0
- AI Layer: ZhipuAI (GLM-4-Flash)
- Deployment: Docker Compose (frontend, backend, database)

Core workflows include:
1. User authentication and authorization
2. Examination creation and submission
3. Score review and publication
4. Practice and wrong-question tracking
5. AI scoring and AI question generation

### 4. Security Analysis Scope
#### 4.1 In Scope
- Authentication and session/token handling
- Role-based access control boundaries
- API input validation and parameter handling
- Exam business logic (submission, state transition, publication)
- Deployment and runtime configuration baseline

#### 4.2 Out of Scope
- Cloud provider internal infrastructure
- Physical device security
- Non-course advanced red-team scenarios

### 5. Methodology and Standards
- Reference standards: OWASP Top 10, OWASP API Security Top 10
- Testing approaches:
  - Manual functional security testing
  - API tampering and edge-case validation
  - Regression verification for critical workflows
  - Runtime evidence collection (logs/screenshots/response records)

### 6. Planned Deliverables
1. Proposal report: architecture, scope, schedule, contribution plan
2. Phase 1 report: vulnerability findings and evidence
3. Phase 2 final report: mitigation strategy, implementation, re-test results
4. Presentation: findings, implementation demo, and conclusion

### 7. Work Schedule
| Stage | Target Output | Planned Completion |
|---|---|---|
| Proposal | Project background and security plan | on/before module deadline |
| Phase 1 | Preliminary vulnerability assessment report | on/before module deadline |
| Phase 2 Final | Mitigation + implementation + re-test | on/before module deadline |
| Presentation | Findings and implementation demonstration | according to module schedule |

### 8. Team Contribution Plan
| Role | Responsibility |
|---|---|
| Project Lead | scope control, timeline management, quality review |
| Security Tester A | authentication/authorization testing |
| Security Tester B | API/input/configuration testing |
| Developer | mitigation implementation and regression verification |
| Documentation & Presentation | report consolidation, slide preparation, demo script |

### 9. Expected Outcomes
- Identify major security weaknesses relevant to system workflows
- Recommend concise and practical mitigations linked to findings
- Implement selected controls and demonstrate measurable improvement
- Provide evidence-backed security report and presentation
