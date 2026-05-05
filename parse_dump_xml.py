#!/usr/bin/env python3
"""
Парсер реестрового XML (rsoc / formatVersion) в CSV с разделителем ';',
как в dump_example.csv: ip|ip|...;domain;url;org;number;date
"""
from __future__ import annotations

import argparse
import csv
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Iterable


def _local_name(tag: str) -> str:
    return tag.rpartition("}")[2] if "}" in tag else tag


def _element_text(elem: ET.Element | None) -> str:
    if elem is None:
        return ""
    return "".join(elem.itertext()).strip()


def iter_content_elements(root: ET.Element) -> Iterable[ET.Element]:
    for el in root.iter():
        if _local_name(el.tag) == "content":
            yield el


def content_row(content_el: ET.Element) -> list[str]:
    decision: ET.Element | None = None
    domain_el: ET.Element | None = None
    url_el: ET.Element | None = None
    ips: list[str] = []
    ipv6s: list[str] = []

    for child in content_el:
        ln = _local_name(child.tag)
        if ln == "decision":
            decision = child
        elif ln == "domain":
            domain_el = child
        elif ln == "url":
            url_el = child
        elif ln == "ip":
            t = _element_text(child)
            if t:
                ips.append(t)
        elif ln == "ipv6":
            t = _element_text(child)
            if t:
                ipv6s.append(t)

    addresses = "|".join(ips + ipv6s)
    domain = _element_text(domain_el)
    url = _element_text(url_el)

    org = number = date = ""
    if decision is not None:
        org = (decision.get("org") or "").strip()
        number = (decision.get("number") or "").strip()
        date = (decision.get("date") or "").strip()

    return [addresses, domain, url, org, number, date]


def parse_xml_file(path: Path) -> ET.Element:
    # Объявление encoding в XML (windows-1251) учитывается при разборе байтов
    with path.open("rb") as f:
        tree = ET.parse(f)
    return tree.getroot()


def write_csv(rows: Iterable[list[str]], out) -> None:
    writer = csv.writer(
        out,
        delimiter=";",
        lineterminator="\n",
        quoting=csv.QUOTE_MINIMAL,
    )
    for row in rows:
        writer.writerow(row)


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Конвертация реестрового XML в CSV (формат dump_example.csv)")
    p.add_argument(
        "input_xml",
        nargs="?",
        type=Path,
        default=Path("dump.xml"),
        help="Входной .xml (по умолчанию: dump.xml)",
    )
    p.add_argument(
        "-o",
        "--output",
        type=Path,
        default="dump.csv",
        help="Выходной .csv (по умолчанию: dump.csv в UTF-8)",
    )
    p.add_argument(
        "-e",
        "--encoding",
        default="utf-8",
        help="Кодировка выходного CSV (по умолчанию utf-8)",
    )
    args = p.parse_args(argv)

    if not args.input_xml.is_file():
        print(f"Файл не найден: {args.input_xml}", file=sys.stderr)
        return 1

    root = parse_xml_file(args.input_xml)
    rows = (content_row(el) for el in iter_content_elements(root))

    if args.output is None:
        write_csv(rows, sys.stdout)
    else:
        with args.output.open("w", encoding=args.encoding, newline="") as f:
            write_csv(rows, f)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
