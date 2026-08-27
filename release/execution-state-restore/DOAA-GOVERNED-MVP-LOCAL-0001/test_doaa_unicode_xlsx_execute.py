import hashlib
import json
import sys
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from doaa_unicode_xlsx_execute import execute


def canon(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


root = Path(__file__).parent / "unicode-xlsx-execution-trial"
root.mkdir(exist_ok=True)
source = root / "input.xlsx"
output = root / "output.xlsx"
output.unlink(missing_ok=True)
worksheet = "بيانات"
proposal = {"kind": "proposal", "execution_authority": "none", "operation": "normalize_unicode_whitespace", "column": "الاسم", "arguments": {}}
sheet = """<worksheet xmlns=\"http://schemas.openxmlformats.org/spreadsheetml/2006/main\"><sheetData><row r=\"1\"><c r=\"A1\" t=\"inlineStr\"><is><t>الاسم</t></is></c><c r=\"B1\" t=\"inlineStr\"><is><t>المبلغ</t></is></c></row><row r=\"2\"><c r=\"A2\" t=\"inlineStr\"><is><t>أحمد&#160;علي&#8239;حسن</t></is></c><c r=\"B2\" t=\"inlineStr\"><is><t>100</t></is></c></row><row r=\"3\"><c r=\"A3\" t=\"inlineStr\"><is><t>سارة</t></is></c><c r=\"B3\" t=\"inlineStr\"><is><t>200</t></is></c></row></sheetData></worksheet>"""
workbook = """<workbook xmlns=\"http://schemas.openxmlformats.org/spreadsheetml/2006/main\" xmlns:r=\"http://schemas.openxmlformats.org/officeDocument/2006/relationships\"><sheets><sheet name=\"بيانات\" sheetId=\"1\" r:id=\"rId1\"/></sheets></workbook>"""
rels = """<Relationships xmlns=\"http://schemas.openxmlformats.org/package/2006/relationships\"><Relationship Id=\"rId1\" Target=\"worksheets/sheet1.xml\" Type=\"worksheet\"/></Relationships>"""
with zipfile.ZipFile(source, "w") as package:
    package.writestr("xl/workbook.xml", workbook)
    package.writestr("xl/_rels/workbook.xml.rels", rels)
    package.writestr("xl/worksheets/sheet1.xml", sheet)

base = {"input_path": str(source), "output_path": str(output), "allowed_root": str(root), "worksheet": worksheet, "proposal": proposal, "human_review": {"status": "accepted_by_human", "execution_authority": "none", "proposal_sha256": hashlib.sha256(canon(proposal).encode()).hexdigest(), "preview_input_sha256": hashlib.sha256(source.read_bytes()).hexdigest(), "audit_record_sha256": "a" * 64}}
result = execute(base)
assert result["status"] == "normalize_unicode_xlsx_executed_safe_file"
assert result["changed_cell_count"] == 1 and result["source_modified"] is False and output.exists()
with zipfile.ZipFile(output) as package:
    text = package.read("xl/worksheets/sheet1.xml").decode("utf-8")
assert "أحمد علي حسن" in text and "100" in text
assert "&#160;" not in text and "&#8239;" not in text
output.unlink()
bad = dict(base)
bad["human_review"] = dict(base["human_review"])
bad["human_review"]["preview_input_sha256"] = "b" * 64
blocked = execute(bad)
assert blocked["status"] == "normalize_unicode_xlsx_blocked" and blocked["reason"] == "preview_source_hash_required_or_mismatch" and not output.exists()
print(json.dumps({"tests": 6, "status": "passed", "arabic_utf8": True, "only_target_column": True, "preview_hash_guard": True, "human_gate": True, "source_unchanged": True}, ensure_ascii=False))
