import hashlib
import json
import sys
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from doaa_algorithm_registry import register
from doaa_audit_log import make_record
from doaa_human_review import review
from doaa_proposal_gate import validate_model_output
from doaa_unicode_xlsx_execute import execute


def canon(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


root = Path(__file__).parent / "unicode-xlsx-unified-trial"
root.mkdir(exist_ok=True)
source = root / "input.xlsx"
output = root / "output.xlsx"
registry = root / "registry.jsonl"
source.unlink(missing_ok=True)
output.unlink(missing_ok=True)
registry.unlink(missing_ok=True)
worksheet = "بيانات"
sheet = """<worksheet xmlns=\"http://schemas.openxmlformats.org/spreadsheetml/2006/main\"><sheetData><row r=\"1\"><c r=\"A1\" t=\"inlineStr\"><is><t>الاسم</t></is></c><c r=\"B1\" t=\"inlineStr\"><is><t>المبلغ</t></is></c></row><row r=\"2\"><c r=\"A2\" t=\"inlineStr\"><is><t>أحمد&#160;علي</t></is></c><c r=\"B2\" t=\"inlineStr\"><is><t>100</t></is></c></row></sheetData></worksheet>"""
workbook = """<workbook xmlns=\"http://schemas.openxmlformats.org/spreadsheetml/2006/main\" xmlns:r=\"http://schemas.openxmlformats.org/officeDocument/2006/relationships\"><sheets><sheet name=\"بيانات\" sheetId=\"1\" r:id=\"rId1\"/></sheets></workbook>"""
rels = """<Relationships xmlns=\"http://schemas.openxmlformats.org/package/2006/relationships\"><Relationship Id=\"rId1\" Target=\"worksheets/sheet1.xml\" Type=\"worksheet\"/></Relationships>"""
with zipfile.ZipFile(source, "w") as package:
    package.writestr("xl/workbook.xml", workbook)
    package.writestr("xl/_rels/workbook.xml.rels", rels)
    package.writestr("xl/worksheets/sheet1.xml", sheet)

request = {"goal": "توحيد الفراغات الخاصة في عمود الاسم", "table_schema": [{"name": "الاسم", "type": "text"}, {"name": "المبلغ", "type": "number"}], "dsl_version": "1.4"}
proposal = {"kind": "proposal", "execution_authority": "none", "operation": "normalize_unicode_whitespace", "column": "الاسم", "arguments": {}, "rationale": "تحويل المحرفين المحددين فقط"}
gate = validate_model_output(proposal, request)
assert gate["status"] == "accepted_proposal"
audit = make_record(request, json.dumps(proposal, ensure_ascii=False), json.dumps(proposal, ensure_ascii=False), gate)
review_payload = {"gate_result": gate, "decision": "accepted_by_human", "explicit_confirmation": True, "audit_record": audit, "audit_record_sha256": audit["record_sha256"], "reviewer_note": "اعتماد يدوي للاختبار"}
human = review(review_payload)
assert human["status"] == "accepted_by_human"
human["preview_input_sha256"] = hashlib.sha256(source.read_bytes()).hexdigest()
payload = {"input_path": str(source), "output_path": str(output), "allowed_root": str(root), "worksheet": worksheet, "proposal": proposal, "human_review": human}
receipt = execute(payload)
assert receipt["status"] == "normalize_unicode_xlsx_executed_safe_file"
registry_proposal = {**proposal, "worksheet": worksheet, "dsl_version": "1.4"}
registered = register(registry, registry_proposal, human, {"status": receipt["status"]})
assert registered["status"] == "registered"
assert output.exists() and registry.exists()
print(json.dumps({"tests": 8, "status": "passed", "gate": gate["status"], "human_review": human["status"], "execution": receipt["status"], "registry": registered["status"], "authority": "none"}, ensure_ascii=False))
