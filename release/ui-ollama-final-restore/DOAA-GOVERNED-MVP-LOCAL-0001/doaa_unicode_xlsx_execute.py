import hashlib
import json
import sys
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

MAIN = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
REL = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
NS = {"m": MAIN, "r": REL}
ET.register_namespace("", MAIN)
ET.register_namespace("r", REL)


def canon(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def sha(value):
    return hashlib.sha256(value if isinstance(value, bytes) else value.encode("utf-8")).hexdigest()


def blocked(reason):
    return {"status": "normalize_unicode_xlsx_blocked", "reason": reason, "execution_started": False, "source_modified": False, "model_execution_authority": "none", "network_request": False}


def col_num(ref):
    number = 0
    for char in ref:
        if not char.isalpha():
            break
        number = number * 26 + ord(char.upper()) - 64
    return number


def shared_values(package):
    if "xl/sharedStrings.xml" not in package.namelist():
        return []
    root = ET.fromstring(package.read("xl/sharedStrings.xml"))
    return ["".join(node.text or "" for node in item.findall(".//m:t", NS)) for item in root.findall("m:si", NS)]


def cell_text(cell, shared):
    cell_type = cell.attrib.get("t")
    if cell_type == "inlineStr":
        return "".join(node.text or "" for node in cell.findall(".//m:t", NS))
    value = cell.find("m:v", NS)
    if value is None:
        return ""
    if cell_type == "s":
        return shared[int(value.text or 0)]
    return value.text or ""


def set_cell_text(cell, value, shared, shared_root):
    if cell.attrib.get("t") == "inlineStr" or shared_root is None:
        cell.set("t", "inlineStr")
        inline = cell.find("m:is", NS)
        if inline is None:
            inline = ET.SubElement(cell, "{" + MAIN + "}is")
        for child in list(inline):
            inline.remove(child)
        ET.SubElement(inline, "{" + MAIN + "}t").text = value
        value_node = cell.find("m:v", NS)
        if value_node is not None:
            cell.remove(value_node)
        return
    cell.set("t", "s")
    if value in shared:
        index = shared.index(value)
    else:
        item = ET.SubElement(shared_root, "{" + MAIN + "}si")
        ET.SubElement(item, "{" + MAIN + "}t").text = value
        shared.append(value)
        index = len(shared) - 1
    value_node = cell.find("m:v", NS)
    if value_node is None:
        value_node = ET.SubElement(cell, "{" + MAIN + "}v")
    value_node.text = str(index)


def execute(payload):
    proposal = payload.get("proposal", {})
    review = payload.get("human_review", {})
    inp = Path(payload.get("input_path", "")).resolve()
    out = Path(payload.get("output_path", "")).resolve()
    root = Path(payload.get("allowed_root", "")).resolve()
    worksheet = payload.get("worksheet")
    if inp.suffix.lower() != ".xlsx" or not inp.is_file():
        return blocked("xlsx_input_required")
    if not root.is_dir() or root not in out.parents or out.exists() or inp == out:
        return blocked("output_policy_violation")
    if proposal.get("operation") != "normalize_unicode_whitespace" or proposal.get("arguments") != {} or not isinstance(proposal.get("column"), str) or not proposal.get("column"):
        return blocked("proposal_not_allowed")
    if proposal.get("execution_authority") != "none" or review.get("status") != "accepted_by_human" or review.get("execution_authority") != "none":
        return blocked("human_acceptance_required")
    if review.get("proposal_sha256") != sha(canon(proposal)):
        return blocked("proposal_hash_mismatch")
    if not isinstance(review.get("audit_record_sha256"), str) or len(review["audit_record_sha256"]) != 64:
        return blocked("audit_hash_required")
    preview_hash = review.get("preview_input_sha256")
    if not isinstance(preview_hash, str) or len(preview_hash) != 64 or preview_hash != sha(inp.read_bytes()):
        return blocked("preview_source_hash_required_or_mismatch")
    if not isinstance(worksheet, str) or not worksheet:
        return blocked("worksheet_not_unique")
    try:
        with ZipFile(inp, "r") as package:
            names = package.namelist()
            shared = shared_values(package)
            workbook = ET.fromstring(package.read("xl/workbook.xml"))
            relationships = ET.fromstring(package.read("xl/_rels/workbook.xml.rels"))
            rel_map = {item.attrib["Id"]: item.attrib["Target"] for item in relationships}
            matches = [item for item in workbook.findall("m:sheets/m:sheet", NS) if item.attrib.get("name") == worksheet]
            if len(matches) != 1:
                return blocked("worksheet_not_unique")
            relationship_id = matches[0].attrib.get("{" + REL + "}id")
            target = rel_map.get(relationship_id, "")
            sheet_path = "xl/" + target.lstrip("/") if not target.startswith("xl/") else target
            sheet_root = ET.fromstring(package.read(sheet_path))
            rows = sheet_root.findall(".//m:sheetData/m:row", NS)
            if not rows:
                return blocked("worksheet_empty")
            headers = [(col_num(cell.attrib.get("r", "")), cell_text(cell, shared)) for cell in rows[0].findall("m:c", NS)]
            matches = [number for number, value in headers if value == proposal["column"]]
            if len(matches) != 1:
                return blocked("target_column_missing")
            target_col = matches[0]
            changed = 0
            before = []
            after = []
            for row in rows[1:]:
                row_before = {}
                row_after = {}
                for cell in row.findall("m:c", NS):
                    number = col_num(cell.attrib.get("r", ""))
                    value = cell_text(cell, shared)
                    row_before[str(number)] = value
                    row_after[str(number)] = value
                    if number == target_col:
                        if cell.attrib.get("t") not in {"s", "inlineStr", "str"}:
                            return blocked("target_cell_not_text")
                        new_value = value.replace("\u00a0", " ").replace("\u202f", " ")
                        if new_value != value:
                            changed += 1
                        row_after[str(number)] = new_value
                before.append(row_before)
                after.append(row_after)
            invariants = {
                "row_count_unchanged": len(before) == len(after),
                "non_target_cells_unchanged": all(all(old[key] == new[key] for key in old if key != str(target_col)) for old, new in zip(before, after)),
                "only_allowed_codepoints_replaced": all(after[index].get(str(target_col), "") == before[index].get(str(target_col), "").replace("\u00a0", " ").replace("\u202f", " ") for index in range(len(before))),
            }
            if not all(invariants.values()):
                return blocked("invariant_failure")
            shared_root = ET.fromstring(package.read("xl/sharedStrings.xml")) if "xl/sharedStrings.xml" in names else None
            shared_for_write = shared_values(package)
            for row in rows[1:]:
                for cell in row.findall("m:c", NS):
                    if col_num(cell.attrib.get("r", "")) == target_col:
                        old_value = cell_text(cell, shared)
                        new_value = old_value.replace("\u00a0", " ").replace("\u202f", " ")
                        if new_value != old_value:
                            set_cell_text(cell, new_value, shared_for_write, shared_root)
            shared_xml = None
            if shared_root is not None:
                shared_root.set("count", str(sum(1 for _ in shared_root.findall("m:si", NS))))
                shared_root.set("uniqueCount", str(len(shared_root.findall("m:si", NS))))
                shared_xml = ET.tostring(shared_root, encoding="utf-8", xml_declaration=True)
            sheet_xml = ET.tostring(sheet_root, encoding="utf-8", xml_declaration=True)
            out.parent.mkdir(parents=True, exist_ok=True)
            with ZipFile(out, "x", compression=ZIP_DEFLATED) as destination:
                for name in names:
                    if name == sheet_path:
                        destination.writestr(name, sheet_xml)
                    elif name == "xl/sharedStrings.xml" and shared_xml is not None:
                        destination.writestr(name, shared_xml)
                    else:
                        destination.writestr(name, package.read(name))
    except Exception:
        return blocked("xlsx_read_failure")
    return {"status": "normalize_unicode_xlsx_executed_safe_file", "operation": proposal["operation"], "worksheet": worksheet, "target_column": proposal["column"], "changed_cell_count": changed, "row_count_before": len(before), "row_count_after": len(after), "invariants": invariants, "input_sha256": sha(inp.read_bytes()), "output_sha256": sha(out.read_bytes()), "execution_timestamp_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"), "source_modified": False, "model_execution_authority": "none", "network_request": False, "execution_started": True, "output_path": str(out)}


def main():
    print(json.dumps(execute(json.loads(sys.stdin.read())), ensure_ascii=False, sort_keys=True, separators=(",", ":")))


if __name__ == "__main__":
    main()
