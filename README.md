# Items Conversion Tool

Automatic converter for Nexo item configurations into structured ItemsAdder-compatible format.

## ✨ Features

- Converts Nexo item configs into ItemsAdder structure
- Automatically detects armor sets
- Generates armor layers dynamically
- Smart namespace detection
- Automatic Spigot material validation
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

* Scan all `.yml` files inside `input/` (And SubFolders)
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

---

## 💭 Planned Features

* Add support to Nexo Furnitures
* Add support to Nexo Blocks

---

> [!WARNING]
> I am not an expert in Python, I will update this repository as I have free time, so it may remain outdated for quite some time.   
