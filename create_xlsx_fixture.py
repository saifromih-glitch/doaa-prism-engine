from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED

root = Path(__file__).parent / "test-runs-excel"
root.mkdir(exist_ok=True)
out = root / "input-arabic-phone.xlsx"
files = {
"[Content_Types].xml": '''<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/><Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/><Override PartName="/xl/worksheets/sheet1.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/><Override PartName="/xl/worksheets/sheet2.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/></Types>''',
"_rels/.rels": '''<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/></Relationships>''',
"xl/workbook.xml": '''<?xml version="1.0" encoding="UTF-8"?><workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"><sheets><sheet name="البيانات" sheetId="1" r:id="rId1"/><sheet name="ملاحظات" sheetId="2" r:id="rId2"/></sheets></workbook>''',
"xl/_rels/workbook.xml.rels": '''<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet1.xml"/><Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet2.xml"/></Relationships>''',
"xl/worksheets/sheet1.xml": '''<?xml version="1.0" encoding="UTF-8"?><worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"><sheetData><row r="1"><c r="A1" t="inlineStr"><is><t>name</t></is></c><c r="B1" t="inlineStr"><is><t>الهاتف</t></is></c><c r="C1" t="inlineStr"><is><t>amount</t></is></c></row><row r="2"><c r="A2" t="inlineStr"><is><t>عميل اختبار 1</t></is></c><c r="B2" t="inlineStr"><is><t>010-123 456</t></is></c><c r="C2" t="inlineStr"><is><t>100</t></is></c></row><row r="3"><c r="A3" t="inlineStr"><is><t>عميل اختبار 2</t></is></c><c r="B3" t="inlineStr"><is><t>011 222-333</t></is></c><c r="C3" t="inlineStr"><is><t>250</t></is></c></row></sheetData></worksheet>''',
"xl/worksheets/sheet2.xml": '''<?xml version="1.0" encoding="UTF-8"?><worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"><sheetData><row r="1"><c r="A1" t="inlineStr"><is><t>لا تعدل</t></is></c></row></sheetData></worksheet>'''
}
with ZipFile(out, "w", ZIP_DEFLATED) as z:
    for name, content in files.items(): z.writestr(name, content)
print(out)
