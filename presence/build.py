#!/usr/bin/env python3
"""UN DESA 2024 bilateral migrant stock: reproducible source-preserving matrix."""
import argparse
import csv
import hashlib
import json
from pathlib import Path
from urllib.request import Request, urlopen

from openpyxl import load_workbook

UN_URL = ("https://www.un.org/development/desa/pd/sites/"
          "www.un.org.development.desa.pd/files/"
          "undesa_pd_2024_ims_stock_by_sex_destination_and_origin.xlsx")
MIRROR_URL = ("https://raw.githubusercontent.com/tigi/2026-migrant-stock/main/"
              "undesa_pd_2024_ims_stock_by_sex_destination_and_origin.xlsx")
SHA256 = "0e10179d05186041a65cf5c6200943b2231701f9c1fd33cbbe21d23b8ea47316"
WORLD = 900


def download_verified(path):
    path = Path(path)
    if path.exists():
        if hashlib.sha256(path.read_bytes()).hexdigest() != SHA256:
            raise ValueError("Cached workbook checksum mismatch")
        return path
    path.parent.mkdir(parents=True, exist_ok=True)
    errors = []
    for url in [UN_URL, MIRROR_URL]:
        try:
            req = Request(url, headers={
                "User-Agent": "Mozilla/5.0 (compatible; global-presence-research/1.0)",
                "Referer": "https://www.un.org/development/desa/pd/content/international-migrant-stock",
            })
            with urlopen(req, timeout=60) as resp:
                data = resp.read(8_000_000)
            digest = hashlib.sha256(data).hexdigest()
            if digest != SHA256:
                raise ValueError("Unexpected SHA256: " + digest)
            path.write_bytes(data)
            return path
        except (ValueError, OSError) as exc:
            errors.append(f"{url}: {exc}")
    raise RuntimeError("Verified UN download failed: " + " | ".join(errors))


def integer(x):
    try:
        if x is None or isinstance(x, bool) or str(x).strip() in ["", "..", "-", "..."]:
            return None
        number = float(str(x).replace(",", ""))
        if not number.is_integer() or number < 0:
            return None
        return int(number)
    except (ValueError, TypeError):
        return None


def is_country(x):
    return x is not None and 0 <= x < 900


def extract(path):
    wb = load_workbook(path, read_only=True, data_only=True)
    try:
        names, pairs, immigrants, emigrants = {}, {}, {}, {}
        worldwide = None
        entries = 0
        # UN Table 1, row 11 header: B destination; E destination M49;
        # F origin; G origin M49; O total both sexes in 2024.
        for row in wb["Table 1"].iter_rows(min_row=12, max_col=15, values_only=True):
            if len(row) < 15:
                continue
            dest, orig, count = integer(row[4]), integer(row[6]), integer(row[14])
            if dest is None or orig is None or count is None:
                continue
            entries += 1
            if is_country(dest) and row[1]:
                names[dest] = str(row[1]).strip().rstrip("*")
            if is_country(orig) and row[5]:
                names[orig] = str(row[5]).strip().rstrip("*")
            if dest == WORLD and orig == WORLD:
                worldwide = count
            elif is_country(dest) and orig == WORLD:
                immigrants[dest] = count
            elif dest == WORLD and is_country(orig):
                emigrants[orig] = count
            elif is_country(dest) and is_country(orig) and dest != orig:
                key = orig, dest
                if key in pairs and pairs[key] != count:
                    raise ValueError(f"Conflicting UN country pair {key}")
                pairs[key] = count
        if worldwide != 304_021_813:
            raise ValueError(f"2024 world anchor incorrect: {worldwide}")
        if len(names) < 200 or len(pairs) < 2000:
            raise ValueError(f"Data too sparse: {len(names)} countries, {len(pairs)} pairs")
        if sum(pairs.values()) > worldwide * 1.01:
            raise ValueError("Double-counting country and aggregate rows")
        return names, pairs, immigrants, emigrants, worldwide, entries
    finally:
        wb.close()


def save(path, columns, rows):
    with Path(path).open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(columns)
        writer.writerows(rows)


def build(source, output):
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    names, pairs, immigrants, emigrants, world, entries = extract(source)
    codes = sorted(names)
    outbound, inbound = {c: 0 for c in codes}, {c: 0 for c in codes}
    for (origin, dest), value in pairs.items():
        outbound[origin] += value
        inbound[dest] += value
    known = sum(pairs.values())
    save(output / "pairs_2024.csv",
         ["origin_m49", "origin", "destination_m49", "destination",
          "resident_estimate", "evidence"],
         ((o, names[o], d, names[d], pairs.get((o, d), 0),
           "UN_reported" if (o, d) in pairs else "not_reported_assumed_zero")
          for o in codes for d in codes if o != d))
    save(output / "reported_pairs_2024.csv",
         ["origin_m49", "origin", "destination_m49", "destination", "residents"],
         ((o, names[o], d, names[d], n) for (o, d), n in sorted(pairs.items())))
    save(output / "country_totals_2024.csv",
         ["m49", "country", "UN_emigrants", "known_abroad", "UN_immigrants",
          "known_from_countries", "destination_unknown_or_unassigned"],
         ((c, names[c], emigrants.get(c, ""), outbound[c], immigrants.get(c, ""),
           inbound[c], max(0, immigrants[c] - inbound[c]) if c in immigrants else "")
          for c in codes))
    info = {
        "reference_date": "2024-07-01",
        "UN_worldwide_residents_outside_origin": world,
        "countries_and_areas": len(codes),
        "off_diagonal_country_pairs": len(codes) * (len(codes) - 1),
        "explicit_UN_country_pair_cells": len(pairs),
        "assigned_country_pair_residents": known,
        "unassigned_to_named_country_pairs": world - known,
        "sum_UN_immigrant_marginals": sum(immigrants.values()),
        "sum_UN_emigrant_marginals": sum(emigrants.values()),
        "rows_parsed": entries,
        "source": UN_URL,
        "source_sha256": SHA256,
        "definition": "2024 immigrant resident stock, primarily birthplace; citizenship otherwise.",
        "warning": "Missing country pairs treated as numeric zero, flagged as assumptions; "
                   "no visitors model and no unassigned-origin redistribution.",
    }
    (output / "summary.json").write_text(json.dumps(info, indent=2) + "\n")
    ordered = sorted(pairs.items(), key=lambda kv: kv[1], reverse=True)[:30]
    lines = [
        "# Global country-to-country migrant resident stock (mid-2024)", "",
        f"UN world total: **{world:,}**. Sum of explicitly named bilateral records: **{known:,}**.",
        f"Named countries/territories: {len(codes)}; reported pairs: {len(pairs)}.",
        f"World total not attributed to individual country pairs: {world-known:,}.", "",
        "| Birth origin | Residence destination | Persons |", "|---|---|---:|",
    ]
    lines.extend(f"| {names[o]} | {names[d]} | {n:,} |" for (o, d), n in ordered)
    lines.extend(["", "Rows marked not_reported_assumed_zero are unobserved, not confirmed zeros.",
                  "Visitors and temporary travel are excluded."])
    (output / "overview.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps(info, indent=2))
    return info


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--source", default="presence/.cache/un_2024.xlsx")
    p.add_argument("--output", default="presence/output")
    a = p.parse_args()
    build(download_verified(a.source), a.output)
