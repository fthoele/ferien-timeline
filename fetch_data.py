#!/usr/bin/env python3
"""Fetch all holiday data for CH + DE, 2024-2028, emit a compact JSON blob."""
import json, subprocess, sys

API = "https://openholidaysapi.org"
YEARS = [2024, 2025, 2026, 2027, 2028]
COUNTRIES = [
    ("CH", "Schweiz – Kantone"),
    ("DE", "Deutschland – Bundesländer"),
]

def get(url):
    out = subprocess.check_output(["curl", "-fsSL", url], timeout=30)
    return json.loads(out)

def name_de(name_arr):
    for n in name_arr:
        if n["language"] == "DE":
            return n["text"]
    return name_arr[0]["text"]

subdivisions = []
holidays = {}

for country, group_label in COUNTRIES:
    print(f"# {country} subdivisions ...", file=sys.stderr)
    subs = get(f"{API}/Subdivisions?countryIsoCode={country}&languageIsoCode=DE")
    for s in subs:
        code = s["code"]
        label = name_de(s["name"])
        subdivisions.append({"code": code, "country": country, "name": label, "group": group_label})

    for s in subs:
        code = s["code"]
        pub_all = []
        sch_all = []
        for y in YEARS:
            params = f"countryIsoCode={country}&languageIsoCode=DE&validFrom={y}-01-01&validTo={y}-12-31&subdivisionCode={code}"
            print(f"  {code} {y}", file=sys.stderr)
            pub = get(f"{API}/PublicHolidays?{params}")
            sch = get(f"{API}/SchoolHolidays?{params}")
            for h in pub:
                pub_all.append([h["startDate"], h["endDate"], name_de(h["name"])])
            for h in sch:
                sch_all.append([h["startDate"], h["endDate"], name_de(h["name"])])
        # dedupe identical entries
        pub_all = sorted({tuple(x) for x in pub_all})
        sch_all = sorted({tuple(x) for x in sch_all})
        holidays[code] = {
            "public": [list(x) for x in pub_all],
            "school": [list(x) for x in sch_all],
        }

# Sportferien supplement for canton Zürich (Volksschule Stadt Zürich) — missing in OpenHolidays.
ZH_SPORTFERIEN = [
    ["2024-02-05", "2024-02-18", "Sportferien (Stadt Zürich)"],
    ["2025-02-10", "2025-02-23", "Sportferien (Stadt Zürich)"],
    ["2026-02-09", "2026-02-22", "Sportferien (Stadt Zürich)"],
    ["2027-02-08", "2027-02-21", "Sportferien (Stadt Zürich)"],
    ["2028-02-07", "2028-02-20", "Sportferien (Stadt Zürich)"],
]
holidays["CH-ZH"]["school"] = sorted(
    {tuple(x) for x in holidays["CH-ZH"]["school"] + ZH_SPORTFERIEN}
)
holidays["CH-ZH"]["school"] = [list(x) for x in holidays["CH-ZH"]["school"]]

out = {"years": YEARS, "subdivisions": subdivisions, "holidays": holidays}
print(json.dumps(out, ensure_ascii=False, separators=(",", ":")))
