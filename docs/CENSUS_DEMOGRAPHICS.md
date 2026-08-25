# HELIOS Census Demographics

Source:
- U.S. Census Bureau 2024 ACS 5-Year Detailed Tables
- Census TIGERweb ACS 2024 tract geometry

Current variables:
- B01001_001E total population
- B01001_003E + B01001_027E population under 5
- B01001 male/female age 65+ categories
- B17001_001E poverty universe
- B17001_002E population below poverty
- B08201_001E households
- B08201_002E households with no vehicle available

Cell allocation:
- tract estimates are allocated to HELIOS cells using polygon overlap area
- this is a derived spatial allocation, not a Census-published cell estimate

Vulnerability index v1:
- under 5: 20%
- age 65+: 30%
- poverty: 30%
- no-vehicle households: 20%

The index is a transparent planning heuristic, not a health diagnosis or causal risk model.

Margins of error:
- tract population MOE is preserved
- grouped age MOEs use root-sum-square approximation
- cell confidence is derived from tract population MOE and allocation weights
