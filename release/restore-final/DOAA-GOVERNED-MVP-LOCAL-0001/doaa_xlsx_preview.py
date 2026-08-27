import hashlib,json,re,sys,zipfile
from pathlib import Path
import xml.etree.ElementTree as ET
NS="{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
REL="{http://schemas.openxmlformats.org/officeDocument/2006/relationships}"
def preview_xlsx(request):
    if not isinstance(request,dict): return {"status":"preview_blocked","reason":"invalid_contract","execution_authority":"none","writes_files":False}
    proposal=request.get("proposal",{}); op=proposal.get("operation"); col=proposal.get("column"); sheet_name=request.get("worksheet")
    if op not in {"remove_ascii_phone_separators","normalize_ascii_spaces","trim_ascii_spaces","tabs_to_ascii_space"} or not isinstance(col,str) or not col or not isinstance(sheet_name,str) or not sheet_name: return {"status":"preview_blocked","reason":"invalid_contract","execution_authority":"none","writes_files":False}
    path=Path(request.get("input_path",""))
    if path.suffix.lower() != ".xlsx" or not path.is_file(): return {"status":"preview_blocked","reason":"input_read_failure","execution_authority":"none","writes_files":False}
    try:
        with zipfile.ZipFile(path) as z:
            wb=ET.fromstring(z.read("xl/workbook.xml")); rels=ET.fromstring(z.read("xl/_rels/workbook.xml.rels"))
            relmap={r.attrib["Id"]:r.attrib["Target"] for r in rels}
            sheets=wb.find(NS+"sheets"); match=[s for s in sheets if s.attrib.get("name")==sheet_name] if sheets is not None else []
            if len(match)!=1: return {"status":"preview_blocked","reason":"worksheet_not_unique","execution_authority":"none","writes_files":False}
            target=relmap.get(match[0].attrib.get(REL+"id"),""); sheet_path="xl/"+target.lstrip("/") if not target.startswith("xl/") else target
            root=ET.fromstring(z.read(sheet_path)); rows=root.findall(".//"+NS+"sheetData/"+NS+"row")
            if not rows: return {"status":"preview_blocked","reason":"worksheet_empty","execution_authority":"none","writes_files":False}
            def cell_value(cell):
                node=cell.find(NS+"v")
                if node is not None and node.text is not None: return node.text
                inline=cell.find(NS+"is")
                return "".join(inline.itertext()) if inline is not None else ""
            headers={c.attrib.get("r","").rstrip("0123456789"):cell_value(c) for c in rows[0].findall(NS+"c")}
            target_col=None
            for letter,value in headers.items():
                if value==col: target_col=letter
            if not target_col: return {"status":"preview_blocked","reason":"target_column_missing","execution_authority":"none","writes_files":False}
            def transform(value):
                if op=="remove_ascii_phone_separators": return value.replace("-","").replace(" ","")
                if op=="normalize_ascii_spaces": return re.sub(r" +"," ",value)
                if op=="trim_ascii_spaces": return value.strip(" ")
                return value.replace("\t"," ")
            changed=0; samples=[]
            for row in rows[1:]:
                for cell in row.findall(NS+"c"):
                    ref=cell.attrib.get("r",""); letter=ref.rstrip("0123456789")
                    if letter!=target_col: continue
                    node=cell.find(NS+"v"); old=cell_value(cell); new=transform(old)
                    if new!=old: changed+=1; samples.append({"cell":ref,"column":col,"before":old,"after":new}) if len(samples)<5 else None
    except Exception: return {"status":"preview_blocked","reason":"input_read_failure","execution_authority":"none","writes_files":False}
    return {"status":"preview_ready","operation":op,"worksheet":sheet_name,"target_column":col,"changed_cell_count":changed,"samples":samples,"input_sha256":hashlib.sha256(path.read_bytes()).hexdigest(),"execution_authority":"none","writes_files":False,"source_modified":False,"execution_started":False}
if __name__=="__main__": print(json.dumps(preview_xlsx(json.loads(sys.stdin.read())),ensure_ascii=False))

