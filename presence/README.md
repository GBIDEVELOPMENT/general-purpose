# Global country-to-country physical presence: 2024 research

This is a standalone analysis under `presence/`, independent of the existing `chat-scheduler` audit log.

**What is modeled now:** 2024-07-01 UN DESA International Migrant Stock by birthplace (or citizenship when birth data are missing) and country of **usual residence**. This is a country-to-country approximation for residents, **not** a count of people physically present abroad at the moment, and excludes visitors, commuters, and temporary tourism.

## Run

```sh
python -m pip install openpyxl==3.1.5
python -m unittest discover -s presence -p 'test_*.py' -v
python presence/build.py
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

## Extending to literal at-any-given-time occupancy

Future visitor estimates belong in a separate, explicitly uncertain layer: UN Tourism annual overnight arrivals multiplied by actual **trip durations / 365**, with origins by **usual residence** not automatically interchangeable with the UN stock's origins by **birthplace**. Pair tourism annual-arrival marginals with bilateral travel data where available and report imputed cells; avoid silently inventing nationality precision. Then subtract residents who are temporarily absent from their host country and account for non-immigrant visitors who are counted in tourism.

The output is a **mid-2024** structural baseline, not a continuously updated live October 2026 tracker.
