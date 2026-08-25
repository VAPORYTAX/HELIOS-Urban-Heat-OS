# HELIOS Intervention Intelligence + Counterfactual Twin

Batch 04 introduces the first complete action layer.

## Intervention catalog
Structured interventions currently include:
- shade structures
- tree canopy expansion
- cool roofs
- cool pavement
- cooling-center activation

Each intervention has:
- category
- effect profile
- cost model
- constraints
- evidence level
- base confidence
- implementation time

## Suitability
Suitability is deterministic and transparent.
It considers:
- road fraction
- shade fraction
- vegetation
- solar exposure
- building fraction
- imperviousness
- vulnerability
- dominant thermal driver
- data quality

## Counterfactual simulation
The engine models changes in:
- TEU
- vulnerable TEU
- projected burden
- intervention cost
- Thermal ROI
- confidence
- uncertainty interval

Intervention effects combine multiplicatively to prevent impossible reductions greater than 100%.

## Scientific boundary
Current counterfactual outputs are tagged `modelled`.
They are not guaranteed causal temperature reductions.
The model is intended for comparative planning and will later be calibrated against observed post-intervention outcomes.

## Next
Batch 05:
- mathematical portfolio optimizer
- multiple objectives
- budget constraints
- equity constraints
- minimum confidence rules
- implementation-time constraints
- Pareto comparison
