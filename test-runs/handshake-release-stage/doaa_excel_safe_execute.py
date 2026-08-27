import hashlib
import json
import sys
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

MAIN = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
REL = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
PKG_REL = "http://schemas.openxmlformats.org/package/2006/relationships"
NS = {"m": MAIN, "r": REL, "p": PKG_REL}
ET.register_namespace("", MAIN)
ET.register_namespace("r", REL)


def canonical(v): return json.dumps(v, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
def sha(v): return hashlib.sha256(v.encode("utf-8") if isinstance(v, str) else v).hexdigest()
def blocked(reason): return {"status":"excel_execution_blocked","reason":reason,"execution_started":False,"model_execution_authority":"none","source_modified":False}
def col_num(ref):
    n = 0
    for ch in ref:
        if ch.isalpha(): n = n * 26 + ord(ch.upper()) - 64
        else: break
    return n

def shared_values(z):
    if "xl/sharedStrings.xml" not in z.namelist(): return []
    root = ET.fromstring(z.read("xl/sharedStrings.xml"))
    return ["".join(t.text or "" for t in si.findall(".//m:t", NS)) for si in root.findall("m:si", NS)]

def cell_text(cell, shared):
    typ = cell.attrib.get("t")
    if typ == "inlineStr": return "".join(t.text or "" for t in cell.findall(".//m:t", NS))
    value = cell.find("m:v", NS)
    if value is None: return ""
    if typ == "s": return shared[int(value.text or 0)]
    return value.text or ""

def set_cell_text(cell, value, shared, shared_root):
    typ = cell.attrib.get("t")
    if typ == "inlineStr":
        inline = cell.find("m:is", NS)
        if inline is None:
            inline = ET.SubElement(cell, "{" + MAIN + "}is")
        for child in list(inline): inline.remove(child)
        ET.SubElement(inline, "{" + MAIN + "}t").text = value
        return
    if typ not in {"s", "str"} and cell.find("m:v", NS) is not None:
        cell.set("t", "s")
    if cell.attrib.get("t") != "s": cell.set("t", "s")
    if value in shared:
        idx = shared.index(value)
    else:
        si = ET.SubElement(shared_root, "{" + MAIN + "}si")
        ET.SubElement(si, "{" + MAIN + "}t").text = value
        shared.append(value); idx = len(shared) - 1
    val = cell.find("m:v", NS)
    if val is None: val = ET.SubElement(cell, "{" + MAIN + "}v")
    val.text = str(idx)

def execute(payload):
    proposal, review = payload.get("proposal"), payload.get("human_review")
    inp, out, root = Path(payload.get("input_path", "")).resolve(), Path(payload.get("output_path", "")).resolve(), Path(payload.get("allowed_root", "")).resolve()
    sheet_name = payload.get("worksheet")
    if inp.suffix.lower() != ".xlsx" or not inp.is_file(): return blocked("xlsx_input_required")
    if not root.is_dir() or root not in out.parents or out.exists() or inp == out: return blocked("output_policy_violation")
    if not isinstance(proposal, dict) or proposal.get("operation") != "remove_ascii_phone_separators" or proposal.get("column") not in {"phone", "الهاتف"} or proposal.get("arguments") != {}: return blocked("proposal_not_allowed")
    if not isinstance(review, dict) or review.get("status") != "accepted_by_human" or review.get("execution_authority") != "none" or proposal.get("execution_authority") != "none": return blocked("human_acceptance_required")
    if review.get("proposal_sha256") != sha(canonical(proposal)): return blocked("proposal_hash_mismatch")
    if not isinstance(review.get("audit_record_sha256"), str) or len(review["audit_record_sha256"]) != 64: return blocked("audit_hash_required")
    with ZipFile(inp, "r") as zin:
        names = zin.namelist(); shared = shared_values(zin)
        wb = ET.fromstring(zin.read("xl/workbook.xml")); rels = ET.fromstring(zin.read("xl/_rels/workbook.xml.rels"))
        rel_map = {r.attrib["Id"]: r.attrib["Target"] for r in rels}
        sheets = wb.findall("m:sheets/m:sheet", NS)
        matches = [s for s in sheets if s.attrib.get("name") == sheet_name]
        if len(matches) != 1: return blocked("worksheet_not_unique")
        rid = matches[0].attrib.get("{" + REL + "}id"); target = rel_map.get(rid, "")
        sheet_path = "xl/" + target.lstrip("/") if not target.startswith("xl/") else target
        sheet_root = ET.fromstring(zin.read(sheet_path))
        rows = sheet_root.findall(".//m:sheetData/m:row", NS)
        if not rows: return blocked("worksheet_empty")
        header_cells = rows[0].findall("m:c", NS)
        header_matches = [(col_num(c.attrib.get("r", "")), cell_text(c, shared)) for c in header_cells if cell_text(c, shared) in {"phone", "الهاتف"}]
        if len(header_matches) != 1: return blocked("phone_header_not_unique")
        target_col, _ = header_matches[0]; changed = 0; before = []; after = []
        for row in rows[1:]:
            record_before = {}; record_after = {}
            for cell in row.findall("m:c", NS):
                col = col_num(cell.attrib.get("r", "")); value = cell_text(cell, shared)
                record_before[str(col)] = value; record_after[str(col)] = value
                if col == target_col:
                    if cell.attrib.get("t") not in {"s", "inlineStr", "str"}: return blocked("target_cell_not_text")
                    new = value.replace(" ", "").replace("-", "") if proposal["operation"] == "remove_ascii_phone_separators" else (value.strip(" ") if proposal["operation"] == "trim_ascii_spaces" else value.replace("\t", " "))
                    if new != value:
                        changed += 1
                    record_after[str(col)] = new
            before.append(record_before); after.append(record_after)
        # Rebuild the target sheet and shared strings from the in-memory XML. For deterministic safety, only write if changes exist.
        ss_root = ET.fromstring(zin.read("xl/sharedStrings.xml")) if "xl/sharedStrings.xml" in names else None
        shared2 = shared_values(zin)
        for row in rows[1:]:
            for cell in row.findall("m:c", NS):
                if col_num(cell.attrib.get("r", "")) == target_col:
                    old = cell_text(cell, shared)
                    new = old.replace(" ", "").replace("-", "")
                    if new != old: set_cell_text(cell, new, shared2, ss_root)
        if ss_root is not None:
            ss_root.set("count", str(sum(1 for _ in ss_root.findall("m:si", NS))))
            ss_root.set("uniqueCount", str(len(ss_root.findall("m:si", NS))))
            shared_xml = ET.tostring(ss_root, encoding="utf-8", xml_declaration=True)
        else: shared_xml = None
        sheet_xml = ET.tostring(sheet_root, encoding="utf-8", xml_declaration=True)
        out.parent.mkdir(parents=True, exist_ok=True)
        with ZipFile(out, "x", compression=ZIP_DEFLATED) as zout:
            for name in names:
                if name == sheet_path: zout.writestr(name, sheet_xml)
                elif name == "xl/sharedStrings.xml" and shared_xml is not None: zout.writestr(name, shared_xml)
                else: zout.writestr(name, zin.read(name))
    return {"status":"excel_executed_safe_file","worksheet":sheet_name,"target_column":proposal["column"],"changed_cell_count":changed,"input_sha256":sha(inp.read_bytes()),"output_sha256":sha(out.read_bytes()),"execution_timestamp_utc":datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),"source_modified":False,"model_execution_authority":"none","network_request":False,"output_path":str(out)}

def main():
    if hasattr(sys.stdin, "reconfigure"):
        sys.stdin.reconfigure(encoding="utf-8")
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    print(canonical(execute(json.loads(sys.stdin.read()))))
if __name__ == "__main__": main()


