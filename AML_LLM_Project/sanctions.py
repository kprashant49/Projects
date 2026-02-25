import xml.etree.ElementTree as ET


def load_un_sanctions(xml_path):

    tree = ET.parse(xml_path)
    root = tree.getroot()

    names = []

    for individual in root.findall(".//INDIVIDUAL"):

        name_parts = []

        for tag in ["FIRST_NAME", "SECOND_NAME", "THIRD_NAME", "FOURTH_NAME"]:
            element = individual.find(tag)
            if element is not None and element.text:
                name_parts.append(element.text.strip())

        if name_parts:
            full_name = " ".join(name_parts)
            names.append(full_name)

    return names