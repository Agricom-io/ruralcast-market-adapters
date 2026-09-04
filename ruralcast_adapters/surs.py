"""SURS pxweb adapter — matrix 0410811S (producer price indices, 2020=100, monthly).

Emits: month, product_code, value, plus fixed provenance columns
(source, source_frequency). Never interpolates.
"""
import argparse, csv, json, sys

API = "https://pxweb.stat.si/SiStatData/api/v1/en/Data/0410811S.px"
SOURCE = "SURS 0410811S"
FREQ = "monthly"

def build_query(products):
    return {
        "query": [
            {"code": "KMETIJSKI PRIDELEK",
             "selection": {"filter": "item", "values": list(products)}},
            {"code": "MERITVE", "selection": {"filter": "item", "values": ["2"]}},
        ],
        "response": {"format": "json"},
    }

def parse_response(payload):
    """pxweb 'json' format -> list of (month, product_code, value). Skips missing values."""
    rows = []
    for d in payload["data"]:
        product, month = d["key"][0], d["key"][1]
        v = d["values"][0]
        if v in ("..", ".", "-", ""):
            continue
        rows.append((month, product, float(v)))
    rows.sort()
    return rows

def fetch(products):
    import requests
    r = requests.post(API, json=build_query(products), timeout=60)
    r.raise_for_status()
    return parse_response(json.loads(r.text.lstrip("﻿")))

def write_csv(rows, out):
    w = csv.writer(out)
    w.writerow(["month", "product_code", "index_2020_100", "source", "source_frequency"])
    for month, product, v in rows:
        w.writerow([month, product, v, SOURCE, FREQ])

def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--products", nargs="+", default=["41000", "61000", "61100", "70000"],
                    help="0410811S product codes (default: fresh vegetables, fresh fruit, dessert apples, wine)")
    ap.add_argument("-o", "--out", default="-")
    a = ap.parse_args(argv)
    rows = fetch(a.products)
    if a.out == "-":
        write_csv(rows, sys.stdout)
    else:
        with open(a.out, "w", newline="") as f:
            write_csv(rows, f)
        print(f"{len(rows)} rows -> {a.out}", file=sys.stderr)

if __name__ == "__main__":
    main()
