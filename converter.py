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
import time

INPUT_DIR = Path("input")
OUTPUT_DIR = Path("output")
CACHE_DIR = Path(".cache")
CACHE_FILE = CACHE_DIR / "materials_cache.yml"
CACHE_DURATION = 60 * 60 * 24  # 24 hours

SPIGOT_MATERIAL_URL = (
    "https://hub.spigotmc.org/stash/projects/SPIGOT/repos/bukkit/raw/"
    "src/main/java/org/bukkit/Material.java"
)

# ---------------------------------------------------
# MATERIAL ENUM WITH SMART CACHE
# ---------------------------------------------------

def fetch_bukkit_materials():
    CACHE_DIR.mkdir(exist_ok=True)

    # ✅ If cache exists and is fresh, use it
    if CACHE_FILE.exists():
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            cache_data = yaml.safe_load(f)

        timestamp = cache_data.get("timestamp", 0)
        if time.time() - timestamp < CACHE_DURATION:
            print("⚡ Using cached material list.")
            return set(cache_data.get("materials", []))

    print("🌐 Downloading Spigot Material enum...")

    try:
        response = requests.get(SPIGOT_MATERIAL_URL, timeout=10)
        response.raise_for_status()
    except Exception as e:
        print(f"⚠ Download failed: {e}")

        if CACHE_FILE.exists():
            print("⚡ Falling back to old cache.")
            with open(CACHE_FILE, "r", encoding="utf-8") as f:
                cache_data = yaml.safe_load(f)
                return set(cache_data.get("materials", []))

        print("⚠ No cache available. Skipping validation.")
        return set()

    materials = set()

    for line in response.text.splitlines():
        line = line.strip()

        if line.startswith("/") or line.startswith("*"):
            continue

        match = re.match(r"([A-Z0-9_]+)\(", line)
        if match:
            materials.add(match.group(1))

    # ✅ Save cache
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        yaml.dump({
            "timestamp": time.time(),
            "materials": sorted(materials)
        }, f)

    print(f"✅ {len(materials)} materials cached.")
    return materials


VANILLA_MATERIALS = fetch_bukkit_materials()
