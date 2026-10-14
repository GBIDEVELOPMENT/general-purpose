#!/usr/bin/env python3
"""Approximate mid-2024 birth-country -> physical-country presence on an average day.

Project UN DESA birth-by-usual-residence stock through a residence-to-tourism
travel model. Birthplaces of visitors are approximated from each departure
country's resident birth-origin composition. Unattributed birthplace retained.
"""
import csv
import json
from collections import defaultdict
from pathlib import Path

BASE_NIGHTS = 4.8


def read(name):
    with Path(name).open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def project(directory):
    directory = Path(directory)
    pairs = read(directory / "pairs_2024.csv")
    countries = read(directory / "country_totals_2024.csv")
    visitors = read(directory / "visitors_average_day_2024.csv")
    pops = read(directory / "origin_population_2024.csv")
    resident = {(int(r["origin_m49"]), int(r["destination_m49"])): float(r["resident_estimate"])
                for r in pairs}
    evidence = {(int(r["origin_m49"]), int(r["destination_m49"])): r["evidence"]
                for r in pairs}
    named = {int(r["m49"]): r["country"] for r in countries}
    iso_to_m49 = {r["iso3"]: int(r["m49"]) for r in pops}
    population = {int(r["m49"]): float(r["2024_population"]) for r in pops}
    immigrant_totals = {int(r["m49"]): float(r["UN_immigrants"] or 0) for r in countries}
    immigrant_named = defaultdict(float)
    birth_by_residence = defaultdict(dict)
    for (birth, residence), stock in resident.items():
        if stock > 0:
            birth_by_residence[residence][birth] = stock
            immigrant_named[residence] += stock
    UNKNOWN = -1
    shares = {}
    for residence in named:
        foreigners = immigrant_totals.get(residence, immigrant_named[residence])
        natives = max(0.0, population.get(residence, 0) - foreigners)
        unknown = max(0.0, foreigners - immigrant_named[residence])
        composition = dict(birth_by_residence[residence])
        composition[residence] = natives
        composition[UNKNOWN] = unknown
        total = sum(composition.values())
        if not total:
            # Countries without OWID population data have no supported
            # birthplace composition; fall back to same-country origin.
            composition = {residence: 1.0}
            total = 1.0
        shares[residence] = {b: n / total for b, n in composition.items() if n > 0}
    delta = defaultdict(float)
    trip_totals = 0
    for r in visitors:
        n = float(r["overnight_visitors_avg_day"])
        if n <= 0:
            continue
        origin = iso_to_m49.get(r["origin_residence_iso3"])
        destination = iso_to_m49.get(r["destination_iso3"])
        if origin is None or destination is None or origin == destination:
            continue
        trip_totals += n
        for birth, fraction in shares[origin].items():
            if birth != origin:
                delta[birth, origin] -= n * fraction
            if birth != destination:
                delta[birth, destination] += n * fraction
    world_known = 0
    uncertain_rows = 0
    with (directory / "physical_presence_by_birth_2024.csv").open(
            "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["birth_origin_m49", "birth_origin", "physical_destination_m49",
                    "physical_destination", "usual_resident_stock",
                    "net_visitors_and_absences", "average_day_physical_estimate",
                    "duration_scenario_low", "duration_scenario_high",
                    "resident_evidence", "travel_evidence"])
        for r in pairs:
            birth, dest = int(r["origin_m49"]), int(r["destination_m49"])
            stock = resident[birth, dest]
            change = delta[birth, dest]
            val = max(0, stock + change)
            extreme1 = max(0, stock + change * (3 / BASE_NIGHTS))
            extreme2 = max(0, stock + change * (10 / BASE_NIGHTS))
            world_known += val
            if evidence[birth, dest] != "UN_reported":
                uncertain_rows += 1
            w.writerow([birth, named[birth], dest, named[dest], round(stock),
                        round(change), round(val), round(min(extreme1, extreme2)),
                        round(max(extreme1, extreme2)), evidence[birth, dest],
                        "population_distance_diaspora_visitor_prior"])
    # The UN's 22m unknown-birth residents remain unknown rather than being
    # treated as citizens or arbitrarily assigned country birth origins.
    unknown_sum = 0
    with (directory / "unknown_birth_presence_2024.csv").open(
            "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["destination_m49", "destination", "UN_unknown_birth_residents",
                    "net_visitor_absence_adjustment", "physical_unknown_birth_estimate"])
        for dest in sorted(named):
            base = max(0.0, immigrant_totals[dest] - immigrant_named[dest])
            value = max(0.0, base + delta[UNKNOWN, dest])
            unknown_sum += value
            w.writerow([dest, named[dest], round(base), round(delta[UNKNOWN, dest]), round(value)])
    data = {
        "reference": "average day of 2024",
        "birthplace_destination_directed_pairs": len(pairs),
        "physical_known_birth_outside_birth_country": round(world_known),
        "physical_unknown_birth_outside_origin": round(unknown_sum),
        "total_estimated_born_abroad_physically": round(world_known + unknown_sum),
        "UN_resident_stock_base": 304021813,
        "visitors_moving_across_borders_on_average_day_in_covered_destinations": round(trip_totals),
        "UN_country_pairs_without_explicit_source_observation": uncertain_rows,
        "method": "subtract travel by host-country residents, add visitors by estimated birth origin; "
                  "birth proportions inferred from UN resident stocks and OWID 2024 population.",
        "warning": "Experimental model. Tourist origin is inferred from destination tourist volumes "
                   "using population, great-circle distance, diaspora. Not a census of persons at "
                   "the moment. 3/10-night scenarios do not measure uncertainty in origin allocation.",
    }
    (directory / "physical_presence_summary.json").write_text(json.dumps(data, indent=2) + "\n")
    print(json.dumps(data, indent=2))
    return data


if __name__ == "__main__":
    project("presence/output")
