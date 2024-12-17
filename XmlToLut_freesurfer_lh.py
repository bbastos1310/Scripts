import xml.etree.ElementTree as ET
import random

def generate_random_color():
    """Gera uma cor aleatória RGB no intervalo 0-255."""
    return random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)

def parse_julich_brain_xml(xml_file, output_lut):
    """
    Parseia o arquivo XML do Julich Brain Atlas e gera um arquivo LUT.

    Args:
        xml_file (str): Caminho para o arquivo XML do atlas.
        output_lut (str): Caminho para o arquivo de saída LUT.
    """
    # Carregar e parsear o arquivo XML
    tree = ET.parse(xml_file)
    root = tree.getroot()

    # Abrir o arquivo LUT para escrita
    with open(output_lut, "w") as lut_file:

        # Iterar pelas estruturas no XML
        for structure in root.find("Structures"):
            num = structure.get("grayvalue")  # Número único da região
            name = structure.text.strip()  # Nome da região

            # Gerar uma cor aleatória
            r, g, b = generate_random_color()

            # Escrever linha no LUT: <num> <name> <R> <G> <B> 0
            lut_file.write(f"{num} {num} {name.replace(' ', '_')}_L {r} {g} {b} 255\n")

    print(f"LUT criado com sucesso: {output_lut}")

# Exemplo de uso
xml_file = "JulichIndex_lh.xml"  # Substitua pelo caminho para o seu arquivo XML
output_lut = "JulichLUT_mrtrix_lh.txt"  # Nome do arquivo LUT de saída

parse_julich_brain_xml(xml_file, output_lut)
