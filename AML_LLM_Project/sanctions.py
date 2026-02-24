import xml.etree.ElementTree as ET

def load_un_sanctions(xml_path):

    tree = ET.parse(xml_path)
    root = tree.getroot()

    names = []

    for individual in root.findall(".//INDIVIDUAL"):
        name = individual.find("FIRST_NAME")
        if name is not None:
            names.append(name.text)

    return names