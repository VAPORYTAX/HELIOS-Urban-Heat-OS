# HELIOS Thermal Intelligence Core

Batch 02 adds deterministic normalized thermal ingestion, month-hour baselines, anomaly, z-score, threshold exceedance, persistence, bounded severity, confidence and spatial hotspot detection.

Truth categories are explicit: `provider`, `observed`, `fixture`, `derived`, `modelled`, `assumed`. Fixture data is never presented as FortyGuard data.

The severity score is transparent and operational, not a causal or trained ML model: 40% intensity, 25% anomaly, 20% exceedance, 15% persistence.

Batch 03 adds population/exposure, vulnerability, TEU, urban context, facilities and thermal-driver attribution.
