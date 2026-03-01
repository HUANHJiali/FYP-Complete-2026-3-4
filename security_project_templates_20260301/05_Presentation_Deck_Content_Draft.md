# ITP4103 Presentation Deck Content (Draft)

## Slide 1 - Title
- Security Assessment and Hardening for Intelligent Examination System
- Module: ITP4103 Security Applications
- Team Members and Roles

## Slide 2 - System Overview
- Architecture: Vue + Django + MySQL + Docker
- Roles: Admin / Teacher / Student
- Core flows: Exam, Practice, AI Scoring, Score Publication

## Slide 3 - Scope and Method
- Scope: authentication, authorization, input validation, business logic, config
- Method: OWASP-based checklist + API tampering + regression scripts
- Evidence: logs, API responses, screenshots, test outputs

## Slide 4 - Finding 1
- Exam creation failure due to datetime format mismatch
- Risk: feature unavailable / data write failure
- Evidence summary and impact

## Slide 5 - Finding 2
- Parameter mismatch in create-from-practice workflow
- Risk: request rejection and workflow interruption
- Evidence summary and impact

## Slide 6 - Finding 3
- Answer persistence and submit timeout issues
- Risk: exam integrity and user trust impact
- Evidence summary and impact

## Slide 7 - Mitigation Implemented
- Datetime normalization and parameter compatibility
- Save-before-switch + submit lock/retry
- Backend submit path optimization and status lifecycle correction

## Slide 8 - Re-test Results
- Full feature smoke: 25/25 pass
- Focused exam workflow regression: 3/3 pass
- Docker runtime verification: all core services healthy

## Slide 9 - Bonus Implementation Value
- Practical code-level mitigations in frontend/backend
- Repeatable demo with one-click validation script
- Improved reliability in critical exam workflow

## Slide 10 - Conclusion and Q&A
- Security testing to implementation closed loop completed
- Key risk reduced and verified
- Next step: expand automated security regression coverage
