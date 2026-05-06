#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Copyright (c) 2026 Rufat Nuriyev, https://rufat.top/, https://dev256.com/

MIT License

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

__author__ = "Rufat Nuriyev"
__copyright__ = "Copyright (c) 2026 Rufat Nuriyev"
__credits__ = ["Rufat Nuriyev"]
__maintainer__ = "Rufat Nuriyev"
__email__ = "info@dev256.com"
__uri__ = "https://rufat.top/"
__urls__ = ["https://rufat.top/", "https://dev256.com/"]
__license__ = "MIT"
__version__ = "1.1"


# from __future__ import annotations

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
