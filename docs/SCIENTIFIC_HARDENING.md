# HELIOS Scientific & Reliability Hardening

## Metric semantics
`vulnerable_teu` remains database-compatible but is now formally interpreted as:
**Vulnerability-Adjusted TEU (VA-TEU)**

It is an amplified burden metric and may exceed ordinary TEU.

## Quality gates
The quality subsystem checks:
- thermal freshness
- fixture/non-live thermal status
- cell-layer completeness
- TEU / VA-TEU invariants
- population/vulnerability bounds

## Audit ledger
Quality-gate failures and warnings are persisted.

## Safety behavior
Until FortyGuard is live, thermal freshness is explicitly review-gated even when the fixture itself is internally consistent.

## Compatibility
No destructive rename is performed in this batch. Existing APIs and data remain compatible.
User-facing layers should display `VA-TEU` while retaining `vulnerable_teu` internally until a later versioned API migration.
