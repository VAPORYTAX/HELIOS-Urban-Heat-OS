# HELIOS Batch 07 — Real Data Integration

Live OSM / Overpass inputs:
- buildings
- roads
- OSM-tagged vegetation / parks
- schools
- healthcare
- vulnerable-care facilities
- transit / bus stops

Urban form is clipped to HELIOS cells and projected into EPSG:32612 for metric calculations.

Truth:
- OSM geometry/tags: observed
- shade fraction proxy: derived
- demographics: unchanged fixture until Census credentials
- thermal: unchanged fixture until FortyGuard credentials

Census ACS adapter is included and key-gated.
FortyGuard remains the primary thermal provider.
