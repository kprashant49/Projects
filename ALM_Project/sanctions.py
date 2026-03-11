"""
sanctions.py — Parse the UN Consolidated Sanctions XML list.

Expected XML schema: CONSOLIDATED_LIST → INDIVIDUALS → INDIVIDUAL
with child elements FIRST_NAME, SECOND_NAME, THIRD_NAME, FOURTH_NAME.

Download the latest list from:
  https://www.un.org/securitycouncil/content/un-sc-consolidated-list
"""

import xml.etree.ElementTree as ET
from pathlib import Path


def load_un_sanctions(xml_path: str | Path) -> list[str]:
    """
    Parse the UN sanctions XML and return a list of full name strings.

    Raises:
        FileNotFoundError: if xml_path does not exist.
        ET.ParseError:     if the file is malformed XML.
    """
    path = Path(xml_path)

    if not path.exists():
        raise FileNotFoundError(
            f"UN sanctions file not found at '{path.resolve()}'.\n"
            "Download it from https://www.un.org/securitycouncil/content/un-sc-consolidated-list "
            "and place it in the data/ directory."
        )

    tree = ET.parse(path)
    root = tree.getroot()

    names      = []
    name_tags  = ["FIRST_NAME", "SECOND_NAME", "THIRD_NAME", "FOURTH_NAME"]

    for individual in root.findall(".//INDIVIDUAL"):
        parts = []

        for tag in name_tags:
            element = individual.find(tag)
            if element is not None and element.text:
                parts.append(element.text.strip())

        if parts:
            names.append(" ".join(parts))

    return names
