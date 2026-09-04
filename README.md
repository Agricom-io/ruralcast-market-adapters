# ruralcast-market-adapters

[![tests](https://github.com/Agricom-io/ruralcast-market-adapters/actions/workflows/ci.yml/badge.svg)](https://github.com/Agricom-io/ruralcast-market-adapters/actions/workflows/ci.yml)

Public-data adapters for **RURALCAST** — community-governed demand-and-price market
intelligence for rural regions (SMART ERA 2nd Open Call, Followers Micro-Pilot; Goričko,
Slovenia). Part of the RURALCAST open-source track (see `ruralcast-ngsi-schema`).

Working adapters for two verified Slovenian public sources:

| Adapter | Source | Frequency | What you get |
|---|---|---|---|
| `surs` | SURS matrix **0410811S** (pxweb API) — producer price indices of agricultural products, 2020=100 | monthly, 2015M01 → current | CSV of index series for selected product groups (fresh vegetables, fresh fruit, dessert apples, wine, …) |
| `dgagri` | DG AGRI agrifood API — Slovenian weekly market prices (cereals endpoint) | weekly, 2015 → current week | CSV of weekly price observations, de-duplicated per week |

Design rules (fixed for RURALCAST): every record carries its **source, source date and
true source frequency** — frequency is never upgraded by interpolation; adapters emit
observations, they never fabricate values for missing weeks.

## Usage

```
pip install requests
python -m ruralcast_adapters.surs   --products 41000 61000 61100 70000 -o surs_monthly.csv
python -m ruralcast_adapters.dgagri --years 2019 2020 2021 2022 2023 2024 2025 2026 -o si_weekly.csv
```

`samples/` holds real output produced by these adapters on 2026-09-04 (public open data,
sources attributed — SURS CC BY 4.0; EU open data), truncated to the last 12 periods.

## Tests

Offline — they validate parsing and week-deduplication logic against bundled fixtures,
so CI never depends on the live endpoints:

```
pip install pytest
python -m pytest tests/
```

## Licence and governance

Apache 2.0 (see `LICENSE`). Docs CC BY 4.0.
Maintainer: Jonas Westphal (Agricom). Deputy: Maria Abdallah (Agricom).

*Planned under the SMART ERA project's 2nd Open Call. SMART ERA has received funding
from the European Union's Horizon Europe research and innovation programme.*
