# ITP4103 Security Applications
## Phase 2 Final Report (Final Submission Draft)
### Security Mitigation, Implementation and Re-test Results

### 1. Final Summary
Following Phase 1 findings, the team implemented targeted controls on both frontend and backend. The focus was to restore exam workflow reliability, improve API robustness, and ensure publish-state consistency.

The implementation includes actual code/configuration changes and repeatable re-tests, satisfying the module’s requirement for practical mitigation and bonus-level implementation evidence.

### 2. Mitigation Matrix
| Finding ID | Root Cause | Implemented Measure | Result |
|---|---|---|---|
| F-01 | inconsistent datetime format handling | server-side datetime normalization + client payload normalization | fixed |
| F-02 | strict key dependency for required parameters | compatible aliases + safer payload assembly | fixed |
| F-03 | incomplete save behavior in answer navigation | save-before-switch and immediate persistence mechanism | fixed |
| F-04 | submit path latency and weak retry tolerance | timeout/retry improvement + optimized submit path | mitigated/fixed |
| F-05 | incorrect status transition at submit stage | lifecycle alignment (pending publish -> published) | fixed |
| F-06 | unsafe partial update logic | field-level guards and validation hardening | fixed |

### 3. Implementation Highlights
1. Input and parameter hardening
- Added normalization and compatibility handling to reduce request fragility.

2. Exam workflow reliability enhancement
- Strengthened answer persistence and submission handling to prevent data loss and duplicate submit behavior.

3. Backend processing optimization
- Adjusted submission processing strategy to reduce timeout risk and improve result clarity.

4. Lifecycle logic correction
- Unified status transition rules between student submit and teacher publish operations.

5. Profile update safety improvement
- Introduced safer partial-update behavior with validation to protect data integrity.

### 4. Re-test Results
| Verification Item | Result |
|---|---|
| Full feature smoke verification | 25/25 passed |
| Focused exam workflow regression | 3/3 passed |
| Post-restart container runtime health | frontend/backend/mysql healthy |

### 5. Evaluation Against Marking Criteria
- Security tests performed: sufficient and relevant scenarios executed with multiple concrete findings.
- Result capture: reproducible findings with evidence records and re-test proof.
- Solution recommendation: each mitigation is directly mapped to identified risk.
- Actual implementation: practical controls implemented and validated.

### 6. Remaining Limitations
- Legacy test scripts still require modernization in some non-core areas.
- Additional long-term security regression coverage is recommended.

### 7. Conclusion
The project demonstrates a full security improvement loop: identification, prioritization, mitigation implementation, and verification. Critical examination workflows are now significantly more stable and aligned with secure operation expectations.
