#!/usr/bin/env python3
"""Exploratory average-day visitor model; separate from UN residence statistics.

Annual *destination* tourist arrivals are from UN Tourism via OWID. Origins are
NOT measured: allocated by population, great-circle distance, and observed
diaspora stock. Visitors classified by home residence, migrants by birthplace.
"""
import argparse
import csv
import json
import math
from collections import defaultdict
from pathlib import Path
from urllib.request import Request, urlopen

import pycountry

ARRIVALS = "https://ourworldindata.org/grapher/international-tourist-trips.csv"
POPULATION = "https://ourworldindata.org/grapher/population.csv"
COORDS = "https://raw.githubusercontent.com/tigi/2026-migrant-stock/main/countries.csv"
DAYS_IN_YEAR = 366
CENTRAL_NIGHTS, LOW_NIGHTS, HIGH_NIGHTS = 4.8, 3.0, 10.0


def fetch_csv(url):
    req = Request(url, headers={"User-Agent": "Mozilla/5.0 (compatible; country-presence-research/1)"})
    with urlopen(req, timeout=90) as f:
        body = f.read(35_000_000).decode("utf-8-sig")
    rows = list(csv.DictReader(body.splitlines()))
    if not rows:
        raise ValueError("Empty CSV: " + url)
    return rows


def series_2024(url, oldest_allowed=2020):
    """Newest positive observation in [oldest_allowed, 2024] for each ISO country.

    UN Tourism reporting is incomplete in 2024; OWID's long-run population
    series itself ends at 2023. Preserve vintage per country, never suggest
    all chosen values are actual 2024 measurements.
    """
    rows = fetch_csv(url)
    first = rows[0]
    columns = [k for k in first if k not in ("Entity", "Code", "Year") and "region" not in k.lower()]
    if len(columns) != 1:
        raise ValueError(f"Ambiguous OWID value field for {url}: {columns}")
    field = columns[0]
    values, vintages = {}, {}
    for r in rows:
        code = r.get("Code", "")
        if len(code) != 3 or not code.isalpha():
            continue
        try:
            yr = int(r["Year"])
            v = float(r[field])
        except (TypeError, ValueError):
            continue
        if (not oldest_allowed <= yr <= 2024 or not v > 0 or
                not math.isfinite(v) or yr < vintages.get(code, 0)):
            continue
        values[code], vintages[code] = v, yr
    return values, vintages


def haversine(a, b):
    lat1, lon1 = map(math.radians, a)
    lat2, lon2 = map(math.radians, b)
    delta_lat, delta_lon = lat2 - lat1, lon2 - lon1
    q = math.sin(delta_lat/2)**2 + math.cos(lat1)*math.cos(lat2)*math.sin(delta_lon/2)**2
    return 6371.0 * 2 * math.asin(min(1, math.sqrt(q)))


def origin_weights(codes, dest, populations, coords, diaspora):
    weights = {}
    for origin in codes:
        if origin == dest:
            continue
        pop = populations.get(origin, 0.0)
        if pop <= 0:
            continue
        # Missing coordinates deliberately receive a long-haul penalty,
        # never a fabricated distance of zero.
        km = (haversine(coords[origin], coords[dest])
              if origin in coords and dest in coords else 6500.0)
        distance_factor = (1 + km / 1000.0) ** -1.45
        # Diaspora is a qualitative affinity proxy, not a measured travel flow.
        affinity = 1 + min(3.0, 50.0 * diaspora.get((origin, dest), 0) / pop)
        weights[origin] = (pop / 1_000_000.0) ** 0.70 * distance_factor * affinity
    return weights


def build(residents_dir, output):
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    residents_dir = Path(residents_dir)
    named, diaspora = {}, {}
    with (residents_dir / "country_totals_2024.csv").open(encoding="utf-8") as f:
        for r in csv.DictReader(f):
            m49 = int(r["m49"])
            country = pycountry.countries.get(numeric=f"{m49:03d}")
            if country is not None:
                named[country.alpha_3] = (m49, r["country"])
    with (residents_dir / "reported_pairs_2024.csv").open(encoding="utf-8") as f:
        for r in csv.DictReader(f):
            o = pycountry.countries.get(numeric=f'{int(r["origin_m49"]):03d}')
            d = pycountry.countries.get(numeric=f'{int(r["destination_m49"]):03d}')
            if o is not None and d is not None:
                diaspora[o.alpha_3, d.alpha_3] = float(r["residents"])
    arrivals, arrival_years = series_2024(ARRIVALS, oldest_allowed=2022)
    populations, population_years = series_2024(POPULATION, oldest_allowed=2020)
    if len(populations) < 150 or len(arrivals) < 80:
        raise ValueError(f'Insufficient OWID coverage: {len(populations)} populations, {len(arrivals)} arrivals')
    coordinates = {}
    for r in fetch_csv(COORDS):
        if len(r["country"]) != 2:
            continue
        country = pycountry.countries.get(alpha_2=r["country"])
        if country is not None and r["latitude"] and r["longitude"]:
            coordinates[country.alpha_3] = float(r["latitude"]), float(r["longitude"])
    codes = sorted(named)
    with (output / "origin_population_2024.csv").open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["iso3", "m49", "country", "2024_population", "source_observation_year"])
        w.writerows((c, named[c][0], named[c][1], round(populations.get(c, 0)), population_years.get(c, "")) for c in codes)
    allocation = {}
    dest_status = {}
    total_annual = 0.0
    for dest in codes:
        annual = arrivals.get(dest)
        if annual is None:
            dest_status[dest] = "no_2022_to_2024_destination_arrivals"
            continue
        weights = origin_weights(codes, dest, populations, coordinates, diaspora)
        weight_sum = sum(weights.values())
        if not weight_sum:
            dest_status[dest] = "no_origin_population_weights"
            continue
        dest_status[dest] = "imputed_from_destination_arrivals_" + str(arrival_years[dest])
        total_annual += annual
        for orig, weight in weights.items():
            allocation[orig, dest] = annual * weight / weight_sum * CENTRAL_NIGHTS / DAYS_IN_YEAR
    with (output / "visitors_average_day_2024.csv").open("w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["origin_residence_iso3", "origin_residence", "destination_iso3",
                         "destination", "overnight_visitors_avg_day",
                         "scenario_low_3_nights", "scenario_high_10_nights",
                         "basis"])
        for orig in codes:
            for dest in codes:
                if orig == dest:
                    continue
                estimate = allocation.get((orig, dest), 0)
                writer.writerow([orig, named[orig][1], dest, named[dest][1],
                                 round(estimate), round(estimate * LOW_NIGHTS / CENTRAL_NIGHTS),
                                 round(estimate * HIGH_NIGHTS / CENTRAL_NIGHTS),
                                 dest_status.get(dest, "missing")])
    with (output / "destination_visitor_marginals.csv").open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["destination", "iso3", "annual_overnight_arrivals", "source_observation_year", "model_avg_daily_visitors", "basis"])
        for d in codes:
            annual = arrivals.get(d)
            w.writerow([named[d][1], d, round(annual) if annual else "", arrival_years.get(d, ""),
                        round(sum(v for (o, dest), v in allocation.items() if dest == d)),
                        dest_status.get(d, "missing")])
    info = {
        "scope": "Average-day visits around 2024, destinations using latest UN Tourism 2022-2024 arrivals",
        "origin_method": "UNMEASURED: country population^0.7 * geographic decay * diaspora affinity",
        "origin_definition": "country of usual residence proxy, NOT country of birth",
        "source_arrivals": ARRIVALS,
        "source_population": POPULATION,
        "source_coordinates": COORDS,
        "available_destination_arrivals": sum(s.startswith("imputed_from_destination_arrivals_") for s in dest_status.values()),
        "destinations_without_arrivals": sum(not s.startswith("imputed_from_destination_arrivals_") for s in dest_status.values()),
        "arrival_source_years": {str(y): sum(1 for dest in codes if dest_status[dest] == "imputed_from_destination_arrivals_" + str(y)) for y in [2022, 2023, 2024]},
        "population_source_years": {str(y): sum(1 for dest in codes if population_years.get(dest) == y) for y in range(2020, 2025)},
        "annual_arrivals_covered": round(total_annual),
        "average_day_visitors_covered": round(sum(allocation.values())),
        "reference_year": 2024, "year_days": DAYS_IN_YEAR,
        "nights_per_trip_model": CENTRAL_NIGHTS,
        "uncertainty": "3 and 10 nights are duration scenarios only, not statistical confidence bounds.",
        "warning": "Visitor ORIGINS are heuristic, not tourism-bilateral observations; "
                   "missing destination observations are NOT zero visitors. "
                   "Do not add directly to birth-origin migrant stock without noting incompatible origin definitions.",
    }
    (output / "visitor_summary.json").write_text(json.dumps(info, indent=2) + "\n")
    print(json.dumps(info, indent=2))


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--residents", default="presence/output")
    p.add_argument("--output", default="presence/output")
    a = p.parse_args()
    build(a.residents, a.output)
