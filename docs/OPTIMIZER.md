# HELIOS Mathematical Portfolio Optimizer

Batch 05 introduces constrained portfolio optimization using Google OR-Tools CP-SAT.

## Supported objectives

- `max_teu`
- `max_vulnerable_teu`
- `max_people`
- `max_roi`
- `balanced`

## Hard constraints

The optimizer can enforce:

- total budget
- minimum confidence
- maximum implementation time
- maximum interventions per cell
- one intervention per category per cell
- feasibility constraints from the intervention engine
- minimum vulnerable-benefit share

## Objective architecture

Candidate benefits are estimated using the existing single-intervention counterfactual engine.
The optimizer selects candidates, then HELIOS runs the selected portfolio through the full scenario simulator.

This intentionally separates:
1. optimization approximation for combinatorial search
2. full counterfactual portfolio evaluation

## Pareto comparison

HELIOS can automatically solve the same budget under five objectives and return the competing portfolios for decision review.

## Scientific boundary

The optimizer does not claim that its mathematical optimum is a guaranteed real-world optimum.
It optimizes the current HELIOS model under explicit constraints and confidence gates.

## Next

Batch 06:
- multi-agent planning/orchestration
- Skeptic/red-team review
- Evidence agent
- Executive synthesis
- recommendation contracts
- human-review gates
