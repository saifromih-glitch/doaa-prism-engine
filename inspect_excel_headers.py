from pathlib import Path
from zipfile import ZipFile
import json
import re
import xml.etree.ElementTree as ET

root = Path(r"C:\Users\saifr\Downloads")
NS = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main", "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships", "p": "http://schemas.openxmlformats.org/package/2006/relationships"}

def text_of(cell, shared):
    kind = cell.attrib.get("t")
    value = cell.find("m:v", NS)
    if value is None: return ""
    if kind == "s":
        idx = int(value.text or 0)
        return shared[idx] if idx < len(shared) else ""
    return value.text or ""

def col_number(ref):
    letters = re.match(r"[A-Z]+", ref or "")
    n = 0
    for ch in (letters.group(0) if letters else ""):
        n = n * 26 + ord(ch) - 64
    return n

results = []
for path in sorted(root.glob("*.xlsx")):
    item = {"file": path.name, "sheets": []}
    try:
        with ZipFile(path) as z:
            shared = []
            if "xl/sharedStrings.xml" in z.namelist():
                tree = ET.fromstring(z.read("xl/sharedStrings.xml"))
                for si in tree.findall("m:si", NS):
                    shared.append("".join(t.text or "" for t in si.findall(".//m:t", NS)))
            workbook = ET.fromstring(z.read("xl/workbook.xml"))
            rels = ET.fromstring(z.read("xl/_rels/workbook.xml.rels"))
            rel_map = {rel.attrib["Id"]: rel.attrib["Target"] for rel in rels}
            for sheet in workbook.findall("m:sheets/m:sheet", NS):
                rid = sheet.attrib.get("{" + NS["r"] + "}id")
                target = rel_map.get(rid, "")
                sheet_path = "xl/" + target.lstrip("/") if not target.startswith("xl/") else target
                root_sheet = ET.fromstring(z.read(sheet_path))
                row = root_sheet.find(".//m:sheetData/m:row", NS)
                cells = {}
                if row is not None:
                    for cell in row.findall("m:c", NS):
                        cells[col_number(cell.attrib.get("r"))] = text_of(cell, shared)
                max_col = max(cells.keys(), default=0)
                item["sheets"].append({"sheet": sheet.attrib.get("name"), "headers": [cells.get(i, "") for i in range(1, max_col + 1)]})
    except Exception as exc:
        item["error"] = type(exc).__name__
    results.append(item)
print(json.dumps(results, ensure_ascii=False, indent=2))
