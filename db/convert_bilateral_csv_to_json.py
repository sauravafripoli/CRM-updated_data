from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path
from typing import Any

BASE_DIR = Path(__file__).resolve().parent
CSV_PATH = BASE_DIR / "INTERNAL_ EU CRM Mapping_Database - Bilateral Partnerships .csv"
OUTPUT_PATH = BASE_DIR / "new.json"


def clean_text(value: Any) -> str:
    if value is None:
        return ""
    return str(value).replace("\r\n", "\n").strip()


def split_areas(value: str) -> Any:
    value = clean_text(value)
    if not value:
        return ""
    parts = [part.strip() for part in value.split(",") if part.strip()]
    return parts if len(parts) > 1 else value


def build_agreement(row: dict[str, str]) -> dict[str, Any]:
    return {
        "typeAgreement": clean_text(row.get("Name/Type of Agreement")),
        "year": clean_text(row.get("Year")),
        "minerals": clean_text(row.get("Interested in Minerals such as/ Notes")),
        "areasCoop": split_areas(clean_text(row.get("Updated areas of cooperation for the Website"))),
        "linkAgreement": clean_text(row.get("Link to Agreement")),
        "sources": clean_text(row.get("Sources: ")),
    }


def build_json(rows: list[dict[str, str]]) -> list[dict[str, Any]]:
    grouped: dict[str, dict[str, list[dict[str, Any]]]] = defaultdict(lambda: defaultdict(list))

    for row in rows:
        partner = clean_text(row.get("Non-African Partner"))
        country = clean_text(row.get("African Country"))
        if not partner or not country:
            continue
        grouped[partner][country].append(build_agreement(row))

    output: list[dict[str, Any]] = []
    for partner, countries in grouped.items():
        partnerships: list[dict[str, Any]] = []
        for country, agreements in countries.items():
            if len(agreements) == 1:
                agreement = agreements[0]
                agreement["country"] = country
                partnerships.append(agreement)
            else:
                partnerships.append({"country": country, "agreements": agreements})

        output.append({"nonafrican": partner, "partnership": partnerships})

    return output


def main() -> None:
    if not CSV_PATH.exists():
        raise FileNotFoundError(f"CSV file not found: {CSV_PATH}")

    with CSV_PATH.open("r", encoding="utf-8-sig", newline="") as csv_file:
        rows = list(csv.DictReader(csv_file))

    data = build_json(rows)

    with OUTPUT_PATH.open("w", encoding="utf-8") as json_file:
        json.dump(data, json_file, indent=4, ensure_ascii=False)
        json_file.write("\n")

    print(f"Wrote {OUTPUT_PATH} with {len(data)} partner groups")


if __name__ == "__main__":
    main()
