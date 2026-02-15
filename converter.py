"""
      ██╗ ██████╗ ████████╗
      ██║ ██╔═══╝ ╚══██╔══╝
      ██║ ██║        ██║   
      ██║ ██║        ██║   
      ██║ ██████╗    ██║   
      ╚═╝ ╚═════╝    ╚═╝
    Items Conversion Tool
    Developed by Nevoeiro_
    © 2026
"""

import yaml
from pathlib import Path
import re
import requests

INPUT_DIR = Path("input")
OUTPUT_DIR = Path("output")

#---------------------------------------------------#
#      AUTOMATIC SEARCH OF SPIGOT MATERIAL ENUM     #
#---------------------------------------------------#


def fetch_bukkit_materials():
    print("🌐 Downloading official Spigot materials list...")

    url = "https://hub.spigotmc.org/stash/projects/SPIGOT/repos/bukkit/raw/src/main/java/org/bukkit/Material.java"
    response = requests.get(url)

    if response.status_code != 200:
        print("⚠ Unable to download enum. Using fallback.")
        return set()

    text = response.text

    materials = set()

    for line in text.splitlines():
        line = line.strip()

        if line.startswith("/") or line.startswith("*"):
            continue

        match = re.match(r"([A-Z0-9_]+)\(", line)
        if match:
            materials.add(match.group(1))

    print(f"✅ {len(materials)} materials found.")
    return materials


VANILLA_MATERIALS = fetch_bukkit_materials()


#---------------------------------------------------#
#                     UTILS                         #
#---------------------------------------------------#


def extract_namespace_and_set(key: str):
    clean = re.sub(
        r"_(boots|chestplate|helmet|leggings|sword|axe|pickaxe|shovel|hoe|shield)$",
        "",
        key,
        flags=re.IGNORECASE,
    )
    parts = clean.split("_", 1)
    if len(parts) == 2:
        return parts[0], parts[1]
    return "custom", clean


def get_namespace_from_filename(filename: str):
    return Path(filename).stem.lower()


def get_namespace_from_path(relative_path: Path):
    parts = relative_path.parts
    if len(parts) > 1:
        return parts[0].lower() 
    return "default"


def convert_to_namespaced_path(path: str):
    path = path.replace("\\", "/")
    VALID_NAMESPACE = re.compile(r"^[a-z0-9_\-.]+$")

    
    if ":" in path:
        namespace, rest = path.split(":", 1)
        if VALID_NAMESPACE.match(namespace):
            return f"{namespace}:{rest}"

    if "/" in path:
        first, rest = path.split("/", 1)
        return f"{first}:{rest}"

    return f"minecraft:{path}"


#---------------------------------------------------#
#                  CONVERSION                       #
#---------------------------------------------------#


def convert_file(data: dict, namespace: str):

    result = {
        "info": {"namespace": namespace},
        "items": {},
    }

    armor_sets = {}

    #---------------------------------------------------#
    #                  1️⃣ PROCESS ITEMS                #
    #---------------------------------------------------#
    for key, item in data.items():

        if not isinstance(item, dict):
            continue

        material = item.get("material", "").upper()

        if VANILLA_MATERIALS and material not in VANILLA_MATERIALS:
            print(f"❌ Material inválido ignorado: {material} ({key})")
            continue

        pack = item.get("Pack", {})
        components = item.get("Components", {})
        equip = components.get("equippable", {})

        cmd = pack.get("custom_model_data")
        model = pack.get("model")

        raw_textures = pack.get("textures") or pack.get("texture")
        textures = []

        if isinstance(raw_textures, list):
            textures = raw_textures
        elif isinstance(raw_textures, str):
            textures = [raw_textures]

        name = item.get("itemname", item.get("name", "<white>Item Sem Nome"))

        entry = {
            "name": name,
            "resource": {
                "generate": False if model else pack.get("generate", True),
                "material": material,
            },
        }

        if cmd:
            entry["resource"]["model_id"] = cmd

        if textures:
            entry["resource"]["texture"] = convert_to_namespaced_path(textures[0])

        if model:
            entry["resource"]["model_path"] = convert_to_namespaced_path(model)

        #---------------------------------------------------#
        #                  ARMOR DETECTION                  #
        #---------------------------------------------------#
        asset_id = equip.get("asset_id")
        slot = equip.get("slot", "").upper()

        if asset_id and slot in {"FEET", "LEGS", "CHEST", "HEAD"}:

            _, set_name = extract_namespace_and_set(asset_id)
            set_name = set_name.split(":")[-1]

            if set_name not in armor_sets:
                armor_sets[set_name] = {
                    "slots": {},
                    "namespace": None,
                    "model_namespace": None,
                }

            texture = entry["resource"].get("texture")

            if texture:
                armor_sets[set_name]["slots"][slot.lower()] = texture

                if ":" in texture:
                    tex_ns = texture.split(":", 1)[0]
                    armor_sets[set_name]["namespace"] = tex_ns

            if model and ":" in entry["resource"].get("model_path", ""):
                model_ns = entry["resource"]["model_path"].split(":", 1)[0]
                armor_sets[set_name]["model_namespace"] = model_ns

            entry["equipment"] = {"id": f"nexo:{set_name}"}

        result["items"][key] = entry

    #---------------------------------------------------#
    #2️⃣ GENERATES EQUIPMENTS (ONLY IF HAVES ARMOR)     #
    #---------------------------------------------------#
    if not armor_sets:
        return result

    result["equipments"] = {}

    for set_name, data_set in armor_sets.items():

        slots = data_set["slots"]

        main_texture = (
            slots.get("chest")
            or slots.get("head")
            or slots.get("legs")
            or slots.get("feet")
        )

        namespace = data_set["namespace"]
        base_path = None

        #------------------------------------------------#
        #            1️⃣ PRIORITY: TEXTURE               #
        #------------------------------------------------#
        if main_texture and ":" in main_texture:

            ns, path = main_texture.split(":", 1)

            # Detects if it is already a layer
            layer_match = re.search(r"(.+)_layer_([12])$", path)

            if layer_match:
                base_path = layer_match.group(1)
                namespace = ns
            else:
                base_path = re.sub(
                    r"_(boots|leggings|chestplate|helmet)$",
                    "",
                    path,
                    flags=re.IGNORECASE,
                )
                namespace = ns

        #------------------------------------------------#
        #2️⃣ FALLBACK: MODEL (gets only the prefix)      #
        #------------------------------------------------#
        if not namespace:
            namespace = data_set["model_namespace"]

        if not base_path:
            base_path = set_name

        #------------------------------------------------#
        #           3️⃣ GENERATES IF POSSIBLE             #
        #------------------------------------------------#
        if namespace and base_path:

            layer_1 = f"{namespace}:{base_path}_layer_1"
            layer_2 = f"{namespace}:{base_path}_layer_2"

            result["equipments"][set_name] = {
                "type": "armor",
                "layer_1": layer_1,
                "layer_2": layer_2,
            }

    # If for some reason it did not generate any valid ones
    if not result["equipments"]:
        result.pop("equipments")

    return result


#---------------------------------------------------#
#                 BATCH PROCESSING                  #
#---------------------------------------------------#


def process_all():

    if not INPUT_DIR.exists():
        print("❌ 'input' folder not found.")
        return

    OUTPUT_DIR.mkdir(exist_ok=True)

    for file in INPUT_DIR.rglob("*.yml"):

        relative_path = file.relative_to(INPUT_DIR)

        namespace = get_namespace_from_path(relative_path)
        print(f"\n🔄 Processing {relative_path} (namespace: {namespace})")

        with open(file, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        if not isinstance(data, dict):
            print(f"⚠ Invalid YAML: {relative_path}")
            continue

        converted = convert_file(data, namespace)

        relative_path = file.relative_to(INPUT_DIR)

        namespace = get_namespace_from_path(relative_path)

        remaining_path = Path(*relative_path.parts[1:])

        output_file = OUTPUT_DIR / namespace / "config" / remaining_path

        output_file.parent.mkdir(parents=True, exist_ok=True)

        with open(output_file, "w", encoding="utf-8") as f:
            yaml.dump(converted, f, allow_unicode=True, sort_keys=False, width=1000)

        print(f"✅ Generated: {output_file}")

    print("\n🎉 Conversion completed successfully.")


if __name__ == "__main__":
    process_all()
