# HELIOS Exposure + Attribution Core

Batch 03 adds the second major decision-intelligence layer.

## Thermal Exposure Units (TEU)

HELIOS separates:

- hazard
- exposure
- vulnerability
- vulnerable exposure
- facility exposure

The initial operational TEU implementation is:

`TEU = hazard_index × population`

and:

`vulnerable_TEU = hazard_index × vulnerable_population × (1 + vulnerability_index)`

These are transparent operational burden metrics, not epidemiological outcome estimates.

## Context

Each thermal cell can store:

- population
- population density
- vulnerable population
- vulnerability index
- vegetation fraction
- impervious fraction
- building fraction
- water fraction
- shade fraction
- road fraction
- solar exposure index
- nighttime retention index
- context data quality
- source/provenance metadata

## Driver attribution

The first attribution engine is deterministic and diagnostic.

Candidate drivers:
- low vegetation
- impervious surface
- solar exposure
- road hardscape
- built form
- nighttime heat retention
- background thermal anomaly

Outputs are normalized contribution scores plus:
- dominant driver
- method version
- input evidence
- confidence

The output explicitly states that it is diagnostic attribution and not causal proof.

## Fixture policy

All Batch 03 Phoenix context and facility records are tagged:
`truth_category = fixture`

They exist only to validate HELIOS logic until external datasets are connected.

## Next: Batch 04

- intervention knowledge base
- intervention suitability
- constraints
- cost models
- counterfactual scenario engine
- uncertainty propagation
