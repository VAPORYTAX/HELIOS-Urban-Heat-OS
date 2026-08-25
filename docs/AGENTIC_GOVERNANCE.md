# HELIOS Agentic Decision + Governance Layer

Batch 06 creates an agentic planning layer without giving language models control over numerical truth.

Agents:
- Scout
- Diagnostician
- Exposure
- Planner
- Skeptic
- Evidence
- Executive

## Design principle

Deterministic spatial, statistical, exposure, counterfactual and optimization engines remain authoritative.

Agents consume structured outputs and generate:
- findings
- challenges
- evidence summaries
- decision status
- recommended action packaging

## Human-review gates

Recommendations are marked for review when:
- confidence is below configured threshold
- fixture data remains in the decision chain
- the Skeptic identifies material uncertainty
- an operational decision lacks real provider/observed inputs

Operational mode can block fixture-backed decisions outright.

## Evidence ledger

Every agent run stores claims linked to:
- source type
- source reference
- truth category
- confidence
- evidence payload

Truth categories remain explicit:
- provider
- observed
- fixture
- derived
- modelled
- assumed

## No private reasoning exposure

The Agent Room/UI should show only:
- agent status
- structured findings
- evidence
- challenges
- final recommendation

It should never expose hidden chain-of-thought.
