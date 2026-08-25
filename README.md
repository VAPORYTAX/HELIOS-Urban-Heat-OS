# HELIOS ThermalWay Intelligence Completion

Fixes the important TEC accounting bug: fastest routes now accumulate thermal exposure
even though travel time remains their optimization objective.

Adds:
- Exposure Budget
- Safe Haven routing to observed facilities
- departure-time optimizer gate (no fabricated hourly forecast)
- corridor heat bottlenecks
- corridor investment priority
- intervention recommendation by corridor
- vulnerable traveler modes

No OSM redownload and no FortyGuard API calls.
