"""DG AGRI agrifood API adapter — Slovenian weekly market prices (cereals endpoint).

De-duplicates to one observation per product/market/week (mean of stage variants).
Emits provenance columns; missing weeks stay missing (no interpolation).
"""
import argparse, csv, sys
from collections import defaultdict

API = "https://api.tech.ec.europa.eu/agrifood/api/cereal/prices"
SOURCE = "DG AGRI agrifood API (cereal/prices)"
FREQ = "weekly"

def parse_price(p):
    """'€221,46' -> 221.46 (EU decimal comma, dot thousands)."""
    return float(p.replace("€", "").replace(".", "").replace(",", "."))

def iso_date(d):
    """'24/08/2026' -> '2026-08-24'."""
    dd, mm, yy = d.split("/")
    return f"{yy}-{mm}-{dd}"

def dedupe_weekly(records):
    """One row per (product, market, beginDate): mean over stage variants."""
    acc = defaultdict(list)
    for r in records:
        key = (r["productName"], r["marketName"], iso_date(r["beginDate"]))
        acc[key].append(parse_price(r["price"]))
    rows = [(d, p, m, round(sum(v) / len(v), 2)) for (p, m, d), v in acc.items()]
    rows.sort()
    return rows

def fetch(years, member_state="SI"):
    import requests
    records = []
    for y in years:
        r = requests.get(API, params={"memberStateCodes": member_state, "years": y}, timeout=60)
        if r.status_code == 404:  # API answers 404 for "no data"
            continue
        r.raise_for_status()
        records.extend(r.json())
    return dedupe_weekly(records)

def write_csv(rows, out):
    w = csv.writer(out)
    w.writerow(["week_begin", "product", "market", "price_eur_t", "source", "source_frequency"])
    for d, p, m, v in rows:
        w.writerow([d, p, m, v, SOURCE, FREQ])

def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--years", nargs="+", type=int, required=True)
    ap.add_argument("--member-state", default="SI")
    ap.add_argument("-o", "--out", default="-")
    a = ap.parse_args(argv)
    rows = fetch(a.years, a.member_state)
    if a.out == "-":
        write_csv(rows, sys.stdout)
    else:
        with open(a.out, "w", newline="") as f:
            write_csv(rows, f)
        print(f"{len(rows)} rows -> {a.out}", file=sys.stderr)

if __name__ == "__main__":
    main()
