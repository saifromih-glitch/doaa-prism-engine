import json,sys,zipfile
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent))
from doaa_xlsx_preview import preview_xlsx
root=Path(__file__).parent/"xlsx-preview-trial"; root.mkdir(exist_ok=True)
inp=root/"input.xlsx"; out=root/"output.xlsx"; out.unlink(missing_ok=True)
xml="""<worksheet xmlns=\"http://schemas.openxmlformats.org/spreadsheetml/2006/main\"><sheetData><row r=\"1\"><c r=\"A1\" t=\"inlineStr\"><is><t>الهاتف</t></is></c><c r=\"B1\" t=\"inlineStr\"><is><t>الاسم</t></is></c></row><row r=\"2\"><c r=\"A2\" t=\"inlineStr\"><is><t> 010-123 </t></is></c><c r=\"B2\" t=\"inlineStr\"><is><t>عميل</t></is></c></row></sheetData></worksheet>"""
wb="""<workbook xmlns=\"http://schemas.openxmlformats.org/spreadsheetml/2006/main\" xmlns:r=\"http://schemas.openxmlformats.org/officeDocument/2006/relationships\"><sheets><sheet name=\"فواتير\" sheetId=\"1\" r:id=\"rId1\"/></sheets></workbook>"""
rels="""<Relationships xmlns=\"http://schemas.openxmlformats.org/package/2006/relationships\"><Relationship Id=\"rId1\" Target=\"worksheets/sheet1.xml\" Type=\"x\"/></Relationships>"""
with zipfile.ZipFile(inp,"w") as z:
    z.writestr("xl/workbook.xml",wb); z.writestr("xl/_rels/workbook.xml.rels",rels); z.writestr("xl/worksheets/sheet1.xml",xml)
r=preview_xlsx({"input_path":str(inp),"output_path":str(out),"worksheet":"فواتير","proposal":{"operation":"trim_ascii_spaces","column":"الهاتف"}})
assert r["status"]=="preview_ready" and r["changed_cell_count"]==1 and r["samples"][0]["after"]=="010-123"
assert r["writes_files"] is False and not out.exists()
bad=preview_xlsx({"input_path":str(inp),"worksheet":"مفقودة","proposal":{"operation":"trim_ascii_spaces","column":"الهاتف"}})
assert bad["status"]=="preview_blocked"
print(json.dumps({"tests":3,"status":"passed","changed_cell_count":r["changed_cell_count"],"output_exists":out.exists()},ensure_ascii=False))
