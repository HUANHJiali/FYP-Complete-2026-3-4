# ITP4103 Project Proposal (Draft)

## 1. Project Background
- Project Title: Intelligent Student Examination System (FYP)
- Project Type: Final Year Project (Web Application)
- Goal: Build a role-based online examination platform with AI-assisted scoring and AI question generation to improve teaching efficiency and student learning outcomes.
- Primary Users: Administrator, Teacher, Student

## 2. Brief System Architecture
- Frontend: Vue 3 + View UI Plus + Vue Router + Vuex
- Backend: Django 4.1.3 (REST-style APIs)
- Database: MySQL 8.0
- AI Integration: ZhipuAI (GLM-4-Flash, OpenAI-compatible API)
- Deployment: Docker Compose (frontend, backend, mysql)

### 2.1 Core Modules
- Authentication & Authorization (JWT)
- Question Bank Management
- Exam Management and Exam Logs
- Practice Paper and Task Center
- Wrong Question Notebook
- AI Scoring & AI Question Generation
- Statistics Dashboard

## 3. Scope of Security Analysis
### 3.1 In Scope
- User login/session flow
- Role-based access controls (admin/teacher/student)
- Exam submission and score publication lifecycle
- Input validation for key APIs
- Deployment/security configuration (DEBUG/CORS/CSRF baseline checks)

### 3.2 Out of Scope
- Third-party cloud provider internal infrastructure
- Stress test under very high concurrency (beyond course scope)
- Physical security controls

## 4. Preliminary Security Risks
- Broken access control between roles
- Insecure input handling in API parameters
- Business logic flaws in exam state transition
- Session/token misuse and timeout handling
- Information leakage via misconfiguration/logging

## 5. Testing Methodology
- Standards: OWASP Top 10 + API Security Top 10
- Methods:
  - Manual testing for logic/authorization flows
  - API replay and parameter tampering
  - Automated smoke verification scripts
  - Regression tests for critical exam workflow
- Evidence:
  - API request/response captures
  - Runtime logs
  - Before/after screenshots
  - Re-test reports

## 6. Work Plan and Milestones
| Milestone | Deliverable | Planned Content |
|---|---|---|
| Proposal | Proposal Document | architecture, scope, schedule, team contribution |
| Phase 1 | Vulnerability Assessment Report | test cases, findings, severity, evidence |
| Phase 2 Final | Final Report | mitigations, implementation, re-test results |
| Presentation | Live Demonstration | vulnerability -> fix -> verification workflow |

## 7. Team Contribution (To be finalized)
| Member | Role | Main Task | Contribution |
|---|---|---|---|
| Member A | Project Lead | planning, integration, final review | TBD |
| Member B | Security Tester | auth/access-control tests | TBD |
| Member C | Security Tester | API/input/configuration tests | TBD |
| Member D | Developer | backend/frontend mitigation implementation | TBD |
| Member E | Documentation | report formatting and presentation | TBD |

## 8. Expected Outcomes
- Identify and prioritize critical security issues in the FYP system.
- Provide practical, relevant mitigation plans.
- Implement selected fixes and validate with re-tests for bonus marks.
