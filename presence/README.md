# Global country-to-country physical presence: 2024 research

This is a standalone analysis under `presence/`, independent of the existing `chat-scheduler` audit log.

**What is modeled now:** 2024-07-01 UN DESA International Migrant Stock by birthplace (or citizenship when birth data are missing) and country of **usual residence**. This is a country-to-country approximation for residents, **not** a count of people physically present abroad at the moment, and excludes visitors, commuters, and temporary tourism.

## Run

```sh
python -m pip install openpyxl==3.1.5 pycountry==24.6.1
python -m unittest discover -s presence -p 'test_*.py' -v
python presence/build.py
python presence/travel.py
python presence/physical.py
```

Source: https://www.un.org/development/desa/pd/content/international-migrant-stock/
Licence: [CC BY 3.0 IGO](https://creativecommons.org/licenses/by/3.0/igo/).
The source file is checked against SHA-256 `0e10179d05186041a65cf5c6200943b2231701f9c1fd33cbbe21d23b8ea47316`. A mirrored copy is accepted only if byte-identical. Raw XLSX is not committed.

## Output semantics

- `output/pairs_2024.csv`: complete country-by-country directed matrix (excludes self); numeric `resident_estimate` and an `evidence` field for every cell.
- `output/reported_pairs_2024.csv`: directly reported UN bilateral country-coded values only.
- `output/country_totals_2024.csv`: source immigrant/emigrant totals and assigned bilateral totals, so unknown origin is visible.
- `output/summary.json` and `output/overview.md`: reconciliation and ranked largest corridors.

`UN_reported` counts are source estimates; `not_reported_assumed_zero` signifies a missing bilateral observation for which we use zero as a conservative working figure. Those zeros can be wrong. The global UN total contains an unknown-origin category which **must not** be distributed as if measured; only named-named pairs contribute to the matrix.

## Experimental visitor and literal physical-presence layers

The travel model reads OWID/UN Tourism destination arrivals (choosing the latest 2022-24 report where possible, otherwise older 2019-21 baseline), and multiplies annual trips by a trial 4.8-night mean / 366. Origins are **unobserved** and therefore estimated with source populations, distance decay and a capped diaspora-affinity factor. Missing tourist-arrival destination totals are left missing, not fabricated. `visitors_average_day_2024.csv` has a **country-of-usual-residence** origin and destination, with `destination_visitor_marginals.csv` documenting source vintages. The original 2024 population base is actually the newest OWID population vintage, generally 2023; see `origin_population_2024.csv` for exact vintage. 

The `physical.py` conversion then uses the UN's measured country-of-birth mix of residents in each departure country to assign visitor birth origins. It subtracts those travelers from their normal foreign residence and adds them at destination. A foreign-born tourist traveling from one foreign country to another remains foreign-born abroad, so that trip does **not** increase the global born-abroad headcount. `physical_presence_by_birth_2024.csv` gives 54,990 birthplace-to-physical-location cells with resident baseline and signed net visitor correction. `unknown_birth_presence_2024.csv` holds unassigned births separately. The traveler duration scenarios (3 versus 10 nights) are **not** statistical uncertainty bounds; origin allocation, data coverage and reporting years introduce bigger uncertainty. No real-time location observation exists here.

The source covers only destinations with usable inbound overnight-arrivals statistics. Omitted destinations and all same-day international travel (including commuters) systematically understate the physical-presence model. Worldwide visitor totals should therefore be treated as scenario-level estimates, with source-year and source-observation warnings preserved.

The output is a **mid-2024** structural baseline, not a continuously updated live October 2026 tracker.
