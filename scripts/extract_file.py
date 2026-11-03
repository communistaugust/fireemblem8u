import os
import re
import yaml
import subprocess

def extract_files():
    for root, dirs, files in os.walk("graphics"):
        for file in files:
            if ".png" not in file and ".json" not in file and ".pal" not in file and ".tsa" not in file and ".bin" not in file and ".tmap" not in file and ".mar" not in file and ".mk" not in file:
                os.remove(os.path.join(root, file))

    with open("baserom.gba", "rb") as f:
        rom_data = f.read()

    with open("graphic_extract.yml", "r") as stream:
        yaml_data = yaml.safe_load(stream)

    yaml_files = yaml_data["files"]

    for file in yaml_files:
        address = int(file["address"], 16) - 0x08000000
        file_content = rom_data[address:address + file["size"]]
        output_path = os.path.join(file["location"], file["file_name"] + "." + file["type"])
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "wb") as extracted:
            extracted.write(file_content)


if __name__ == "__main__":
    extract_files()