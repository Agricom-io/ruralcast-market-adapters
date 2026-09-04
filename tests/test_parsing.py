import io, json
from ruralcast_adapters import surs, dgagri

def test_surs_parse_skips_missing_and_sorts():
    payload = {"data": [
        {"key": ["61000", "2016M02", "2"], "values": ["79.27"]},
        {"key": ["61000", "2016M01", "2"], "values": ["79.63"]},
        {"key": ["61000", "2016M03", "2"], "values": [".."]},
    ]}
    rows = surs.parse_response(payload)
    assert rows == [("2016M01", "61000", 79.63), ("2016M02", "61000", 79.27)]

def test_surs_query_shape():
    q = surs.build_query(["41000"])
    assert q["query"][0]["selection"]["values"] == ["41000"]
    assert q["response"]["format"] == "json"

def test_dgagri_price_and_date_parsing():
    assert dgagri.parse_price("€221,46") == 221.46
    assert dgagri.parse_price("€1.234,50") == 1234.50
    assert dgagri.iso_date("24/08/2026") == "2026-08-24"

def test_dgagri_dedupes_stage_variants_to_one_week():
    recs = [
        {"productName": "P", "marketName": "M", "beginDate": "01/01/2024", "price": "€200,00"},
        {"productName": "P", "marketName": "M", "beginDate": "01/01/2024", "price": "€210,00"},
        {"productName": "P", "marketName": "M", "beginDate": "08/01/2024", "price": "€220,00"},
    ]
    rows = dgagri.dedupe_weekly(recs)
    assert rows == [("2024-01-01", "P", "M", 205.0), ("2024-01-08", "P", "M", 220.0)]

def test_csv_writers():
    out = io.StringIO()
    surs.write_csv([("2016M01", "61000", 79.63)], out)
    assert "month,product_code,index_2020_100,source,source_frequency" in out.getvalue()
    out2 = io.StringIO()
    dgagri.write_csv([("2024-01-01", "P", "M", 205.0)], out2)
    assert "week_begin,product,market,price_eur_t,source,source_frequency" in out2.getvalue()
