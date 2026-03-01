# ITP4103 Phase 1 Report (Draft) - Vulnerability Assessment

## 1. Executive Summary
This phase evaluates the security posture of the Intelligent Student Examination System. The focus is on authentication, authorization, input handling, business logic integrity, and deployment configuration. Initial testing identified several high-impact issues in exam workflow reliability and API parameter handling.

## 2. Test Environment
- Deployment: Docker Compose (frontend + backend + mysql)
- Backend APIs: Django 4.1.3
- Frontend: Vue 3
- Test Roles: admin / teacher / student
- Sample Accounts: admin, teacher, student

## 3. Methodology
- OWASP-based checklist for web/API testing
- Role-switch and privilege boundary validation
- API parameter tampering and edge-value tests
- Business workflow verification for exam submission and score publication

## 4. Test Case Summary
| ID | Category | Objective | Result | Severity |
|---|---|---|---|---|
| TC-01 | Input Validation | Validate datetime payload format in exam creation | Fail (found) | High |
| TC-02 | API Parameters | Validate required parameter compatibility in create-from-practice flow | Fail (found) | High |
| TC-03 | Business Logic | Validate answer persistence during question switching | Fail (found) | High |
| TC-04 | Performance/Availability | Validate exam submit timeout behavior | Fail (found) | High |
| TC-05 | Workflow Integrity | Validate status lifecycle for teacher score publication | Fail (found) | Medium |
| TC-06 | Profile Update Integrity | Validate partial update on user profile | Fail (found) | Medium |

## 5. Key Findings

### F-01: Invalid datetime handling breaks exam creation
- Severity: High
- Affected Area: create exam from practice paper
- Impact: exam creation failure with database "Data too long" errors
- Evidence: API error and database column mismatch behavior
- Initial Root Cause: inconsistent datetime string format before persistence

### F-02: Required parameter mismatch in API request
- Severity: High
- Affected Area: create_from_practice_paper endpoint
- Impact: request rejected due to missing parameters under mixed naming styles
- Evidence: backend response "missing required parameters"
- Initial Root Cause: strict key expectation without alias compatibility

### F-03: Answer loss when navigating questions
- Severity: High
- Affected Area: student answering page
- Impact: user answer may be lost before submit, affecting exam fairness and data integrity
- Evidence: switch-question reproduction, inconsistent local state persistence
- Initial Root Cause: incomplete save-before-switch mechanism

### F-04: Exam submission timeout and unstable retry
- Severity: High
- Affected Area: answer submit API and backend processing path
- Impact: submission failure perception, user anxiety, risk of repeated submits
- Evidence: timeout prompts and local-save fallback
- Initial Root Cause: heavy submit path and insufficient timeout/retry strategy

### F-05: Status lifecycle mismatch blocks score publication
- Severity: Medium
- Affected Area: student submit -> teacher publish workflow
- Impact: teacher-side publish action not aligned with expected status
- Evidence: record not appearing in publish-ready state
- Initial Root Cause: wrong status value assignment during submit

### F-06: Unsafe partial update behavior in profile endpoint
- Severity: Medium
- Affected Area: user profile update
- Impact: possible null overwrite risk on required fields
- Evidence: partial update behavior inconsistency
- Initial Root Cause: missing field-level guard and validation

## 6. Risk Prioritization
| Finding | Likelihood | Impact | Priority |
|---|---|---|---|
| F-01 | High | High | P1 |
| F-02 | High | High | P1 |
| F-03 | High | High | P1 |
| F-04 | High | High | P1 |
| F-05 | Medium | Medium | P2 |
| F-06 | Medium | Medium | P2 |

## 7. Interim Conclusion
Phase 1 confirms multiple exploitable reliability and logic weaknesses in core examination flows. Phase 2 will prioritize remediation of P1 findings and provide implementation evidence and re-test proof.
