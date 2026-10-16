"""Probe the CFPB API: where does the narrative text live?"""

import json
import urllib.parse
import urllib.request

BASE = "https://www.consumerfinance.gov/data-research/consumer-complaints/search/api/v1/"

# Probe 1: one raw search hit, ALL keys (not just _source)
params = {
    "size": 1,
    "no_aggs": "true",
    "has_narrative": "true",
    "date_received_min": "2026-01-01",
    "product": "Credit card",
}
url = BASE + "?" + urllib.parse.urlencode(params)
with urllib.request.urlopen(url) as resp:
    payload = json.load(resp)
hit = payload["hits"]["hits"][0]
print("hit keys:", sorted(hit.keys()))
print("source keys:", sorted(hit["_source"].keys()))
cid = hit["_source"]["complaint_id"]
print("complaint_id:", cid)
print()

# Probe 2: detail endpoint for that one complaint
url2 = BASE + str(cid)
with urllib.request.urlopen(url2) as resp:
    detail = json.load(resp)
print("detail top-level keys:", sorted(detail.keys()))
src = detail.get("_source", detail)
if "hits" in detail:
    src = detail["hits"]["hits"][0]["_source"]
print("detail source keys:", sorted(src.keys()))
text = src.get("complaint_what_happened", "")
print("narrative present:", bool(text))
print("first 200 chars:", repr(text[:200]))
