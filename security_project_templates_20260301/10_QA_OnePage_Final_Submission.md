# ITP4103 Security Applications
## One-page Q&A (Final Submission Draft)

### Q1. Why is this finding considered high severity?
Because it directly affects core exam operations (creation, submission, publication), causing service disruption, data integrity risk, and potential fairness concerns.

### Q2. Why did your team choose these mitigation measures?
Each measure is mapped to a specific root cause and designed to be practical within project constraints, with minimal side effects and clear verification criteria.

### Q3. How do you prove the fixes are effective?
We performed repeatable re-tests after implementation, including full feature smoke checks and focused workflow regression tests, with pass results and runtime health evidence.

### Q4. What bonus-level implementation did you complete?
We implemented code-level fixes in frontend and backend for input normalization, parameter compatibility, submission reliability, workflow status correction, and data update safety.

### Q5. What limitations remain?
Some legacy scripts require modernization and broader automated security regression can be expanded in future iterations.

### Q6. If given more time, what is the next step?
Expand automated security tests for authorization and injection scenarios, strengthen secure defaults, and integrate continuous security checks into deployment pipelines.
