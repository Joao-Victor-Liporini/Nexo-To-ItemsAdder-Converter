# Items Conversion Tool

Automatic converter for Nexo item configurations into structured ItemsAdder-compatible format.

## ✨ Features

- Converts legacy item configs into standardized structure
- Automatically detects armor sets
- Generates armor layers dynamically
- Smart namespace detection
- Automatic Spigot material validation
- 24-hour material enum cache system
- Safe fallback system if download fails

---

## 📦 Requirements

- Python 3.9+
- PyYAML
- Requests

Install dependencies:

```bash
pip install pyyaml requests
````

---

## 📂 Folder Structure

```
project/
│
├── input/
│   └── your_files.yml
│
├── output/
│
├── converter.py
```

---

## 🚀 Usage

Simply run:

```bash
python converter.py
```

The script will:

* Scan all `.yml` files inside `input/`
* Convert them
* Generate output in:

```
output/<namespace>/config/<original_structure>
```

---

## 🧠 Armor Logic

Armor sets are automatically detected from:

* `Components.equippable.asset_id`
* Texture namespace
* Model namespace fallback

Layers are generated as:

```
<namespace>:<base_path>_layer_1
<namespace>:<base_path>_layer_2
```

If no armor is detected in the file, the `equipments` section is not generated.

---

## ⚡ Material Validation

The script downloads the official Spigot `Material.java` enum.

To avoid downloading on every run:

* A local cache is stored in `.cache/materials_cache.yml`
* Cache expires after 24 hours
* If download fails, the script falls back to cached data

---

