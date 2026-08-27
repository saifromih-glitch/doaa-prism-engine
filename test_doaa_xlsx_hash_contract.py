import hashlib,json,sys,zipfile
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent))
from doaa_excel_safe_execute import execute
def canon(v): return json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(",",":"))
root=Path(__file__).parent/"xlsx-hash-contract-trial"; root.mkdir(exist_ok=True)
inp=root/"input.xlsx"; out=root/"output.xlsx"; out.unlink(missing_ok=True)
xml="""<worksheet xmlns=\"http://schemas.openxmlformats.org/spreadsheetml/2006/main\"><sheetData><row r=\"1\"><c r=\"A1\" t=\"inlineStr\"><is><t>الهاتف</t></is></c></row><row r=\"2\"><c r=\"A2\" t=\"inlineStr\"><is><t>010-123</t></is></c></row></sheetData></worksheet>"""
wb="""<workbook xmlns=\"http://schemas.openxmlformats.org/spreadsheetml/2006/main\" xmlns:r=\"http://schemas.openxmlformats.org/officeDocument/2006/relationships\"><sheets><sheet name=\"فواتير\" sheetId=\"1\" r:id=\"rId1\"/></sheets></workbook>"""
rels="""<Relationships xmlns=\"http://schemas.openxmlformats.org/package/2006/relationships\"><Relationship Id=\"rId1\" Target=\"worksheets/sheet1.xml\" Type=\"x\"/></Relationships>"""
with zipfile.ZipFile(inp,"w") as z:
    z.writestr("xl/workbook.xml",wb); z.writestr("xl/_rels/workbook.xml.rels",rels); z.writestr("xl/worksheets/sheet1.xml",xml)
proposal={"kind":"proposal","execution_authority":"none","operation":"remove_ascii_phone_separators","column":"الهاتف","arguments":{}}
base={"input_path":str(inp),"output_path":str(out),"allowed_root":str(root),"worksheet":"فواتير","proposal":proposal,"human_review":{"status":"accepted_by_human","execution_authority":"none","audit_record_sha256":"a"*64}}
missing=execute(base)
assert missing["status"]=="excel_execution_blocked" and missing["reason"]=="proposal_hash_mismatch"
base["human_review"]["proposal_sha256"]="b"*64; mismatch=execute(base)
assert mismatch["status"]=="excel_execution_blocked" and mismatch["reason"]=="proposal_hash_mismatch"
assert not out.exists()
base["human_review"]["proposal_sha256"]=hashlib.sha256(canon(proposal).encode()).hexdigest(); accepted=execute(base)
assert accepted["status"]=="excel_executed_safe_file" and out.exists()
print(json.dumps({"tests":4,"status":"passed","missing_hash":"blocked","mismatch_hash":"blocked","accepted":"executed"},ensure_ascii=False))




