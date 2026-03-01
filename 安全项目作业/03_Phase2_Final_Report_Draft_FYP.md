# ITP4103 Phase 2 Final Report (Draft) - Mitigation and Implementation

## 1. Final Summary
Based on Phase 1 findings, targeted mitigations were implemented on both frontend and backend. Critical exam workflow issues were fixed and validated through smoke checks and focused regression tests.

## 2. Mitigation Mapping
| Finding ID | Root Cause | Implemented Measure | Status |
|---|---|---|---|
| F-01 | inconsistent datetime format | normalize datetime input before DB write | Implemented |
| F-02 | strict parameter key dependency | add compatible parameter aliases and safer payload assembly | Implemented |
| F-03 | answer state not persisted reliably | add save-before-switch and current-answer persistence | Implemented |
| F-04 | heavy submit path and weak retry | optimize submit logic, overwrite mode, timeout and retry improvement | Implemented |
| F-05 | status transition mismatch | align status lifecycle: submit -> pending publish -> published | Implemented |
| F-06 | unsafe partial updates | field-safe partial update and validation checks | Implemented |

## 3. Implementation Highlights

### I-01: Robust exam creation input handling
- Backend normalizes datetime text to DB-compatible format.
- Frontend sends normalized datetime payload.
- Result: no more "Data too long" creation failure for valid cases.

### I-02: Compatible API parameter handling
- Backend accepts key aliases for paper/teacher/grade IDs.
- Frontend strengthens payload field extraction.
- Result: create-from-practice request compatibility improved.

### I-03: Reliable answer persistence and submission
- Frontend introduces immediate persistence and save-before-switch.
- Submit flow protected with lock and enhanced retry conditions.
- API timeout increased for long-running submission scenarios.
- Result: reduced answer-loss and duplicate-submit risk.

### I-04: Backend submit path redesign
- Overwrite mode prevents duplicate answer accumulation.
- Objective questions can be scored quickly; subjective items marked pending manual review by default.
- Result: lower submit latency and clearer grading state.

### I-05: Score publication lifecycle correction
- Student submit now enters pending-publish state.
- Teacher publish action transitions to published state.
- Result: teacher UI and backend status logic become consistent.

### I-06: Safer user profile update
- Partial updates now guard required fields and parse/validate critical inputs.
- Result: lower risk of accidental data corruption.

## 4. Re-test Evidence (Summary)
| Verification Item | Result |
|---|---|
| Full feature smoke check | 25/25 pass |
| Exam flow focused regression | 3/3 pass |
| Container health after restart | frontend/backend/mysql healthy |

## 5. Security Improvement Outcome
- Exam core workflow is more stable and auditable.
- Submission and publication chain is logically consistent.
- API robustness improved for common malformed/variant inputs.
- Operational demo readiness achieved with one-click validation script.

## 6. Remaining Risks and Future Work
- Legacy scripts may still contain route/model mismatch and should be modernized.
- Add more automated security regression cases for authorization and injection scenarios.
- Continue hardening on rate-limit tuning and secure-by-default configuration review.

## 7. Conclusion
The project moved from vulnerability discovery to practical mitigation with measurable re-test results. This fulfills the course requirement for relevant security testing and solution implementation, including demonstrable bonus-level implementation work.
