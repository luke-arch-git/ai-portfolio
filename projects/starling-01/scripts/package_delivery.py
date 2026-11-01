import json
import struct
import zipfile
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

BASE = Path(__file__).resolve().parents[1]
OUT = BASE / "output"

required = [
    "STARLING-01.blend",
    "STARLING-01.glb",
    "STARLING-01_Hero_2048.png",
    "STARLING-01_Turntable_10s.mp4",
    "Front_view.png",
    "Side_view.png",
    "Back_view.png",
    "Top_view.png",
    "Bottom_view.png",
]
for name in required:
    path = OUT / name
    if not path.is_file() or path.stat().st_size == 0:
        raise RuntimeError(f"Missing deliverable: {name}")

with Image.open(OUT / "STARLING-01_Hero_2048.png") as hero:
    if hero.size != (2048, 2048):
        raise RuntimeError(f"Unexpected hero dimensions: {hero.size}")

raw = (OUT / "STARLING-01.glb").read_bytes()
magic, version, declared_length = struct.unpack_from("<4sII", raw, 0)
if magic != b"glTF" or version != 2 or declared_length != len(raw):
    raise RuntimeError("Invalid GLB header")
json_length, chunk_type = struct.unpack_from("<I4s", raw, 12)
if chunk_type != b"JSON":
    raise RuntimeError("Missing GLB JSON chunk")
gltf = json.loads(raw[20:20 + json_length])
triangles = 0
vertices = 0
for mesh in gltf.get("meshes", []):
    for primitive in mesh.get("primitives", []):
        if "indices" in primitive:
            triangles += gltf["accessors"][primitive["indices"]]["count"] // 3
        if "POSITION" in primitive["attributes"]:
            vertices += gltf["accessors"][primitive["attributes"]["POSITION"]]["count"]

font_path = Path("/System/Library/Fonts/Supplemental/Arial.ttf")
if font_path.exists():
    title_font = ImageFont.truetype(str(font_path), 32)
    label_font = ImageFont.truetype(str(font_path), 19)
else:
    title_font = label_font = ImageFont.load_default()
sheet = Image.new("RGB", (1800, 1370), "#E8E3DA")
draw = ImageDraw.Draw(sheet)
draw.text((45, 25), "STARLING—01  /  STRUCTURAL INSPECTION", fill="#243137", font=title_font)
placements = [
    ("Front_view.png", "01 / FRONT", (0, 85)),
    ("Side_view.png", "02 / SIDE", (600, 85)),
    ("Back_view.png", "03 / BACK", (1200, 85)),
    ("Top_view.png", "04 / TOP", (300, 715)),
    ("Bottom_view.png", "05 / BOTTOM", (900, 715)),
]
for filename, label, (x, y) in placements:
    with Image.open(OUT / filename) as source:
        image = source.convert("RGB").resize((600, 600), Image.Resampling.LANCZOS)
        sheet.paste(image, (x, y))
    draw.rectangle((x, y + 600, x + 600, y + 630), fill="#E8E3DA")
    draw.text((x + 18, y + 603), label, fill="#586069", font=label_font)
sheet.save(OUT / "STARLING-01_Views.png", optimize=True)

report = {
    "asset": "STARLING-01 / 星际信使",
    "hero_dimensions": [2048, 2048],
    "inspection_view_dimensions": [1400, 1400],
    "glb": {
        "version": version,
        "meshes": len(gltf.get("meshes", [])),
        "materials": len(gltf.get("materials", [])),
        "vertices": vertices,
        "triangles": triangles,
        "extensions": gltf.get("extensionsUsed", []),
    },
    "video": {"duration_seconds": 10, "dimensions": [768, 768], "fps": 24, "frames": 240},
    "files": {name: (OUT / name).stat().st_size for name in required},
}
(OUT / "delivery_report.json").write_text(json.dumps(report, indent=2, ensure_ascii=False))

files = [OUT / name for name in required]
files += [
    OUT / "STARLING-01_Views.png",
    OUT / "Interactive_Preview.png",
    OUT / "Turntable_Contact_Sheet.png",
    OUT / "asset_manifest.json",
    OUT / "delivery_report.json",
    BASE / "scripts" / "build_starling.py",
    BASE / "scripts" / "render_starling.py",
    BASE / "scripts" / "package_delivery.py",
]
for name in ("index.html", "styles.css", "preview.js", "app.js", "serve.py", "package.json", "package-lock.json"):
    path = BASE / "preview" / name
    if path.exists():
        files.append(path)
archive = BASE / "STARLING-01_Delivery.zip"
with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as zf:
    for path in files:
        zf.write(path, Path("STARLING-01") / path.relative_to(BASE))
print(json.dumps(report, indent=2, ensure_ascii=False))
print(f"DELIVERY_ZIP {archive} ({archive.stat().st_size / 1024 / 1024:.1f} MB)")
