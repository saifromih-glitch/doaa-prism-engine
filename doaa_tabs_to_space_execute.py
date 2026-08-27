import csv, hashlib, json, sys
from datetime import datetime, timezone
from pathlib import Path

def canon(v): return json.dumps(v, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
def sha(v): return hashlib.sha256(v.encode("utf-8") if isinstance(v,str) else v).hexdigest()
def blocked(reason): return {"status":"tabs_to_space_blocked","reason":reason,"execution_started":False,"source_modified":False,"model_execution_authority":"none","network_request":False}
def execute(payload):
    p=payload.get("proposal",{}); r=payload.get("human_review",{}); inp=Path(payload.get("input_path","")).resolve(); out=Path(payload.get("output_path","")).resolve(); root=Path(payload.get("allowed_root","")).resolve()
    if inp.suffix.lower() != ".csv" or not inp.is_file(): return blocked("csv_input_required")
    if not root.is_dir() or root not in out.parents or out.exists() or inp==out: return blocked("output_policy_violation")
    if p.get("operation")!="tabs_to_ascii_space" or p.get("arguments")!={} or not isinstance(p.get("column"),str) or not p.get("column"): return blocked("proposal_not_allowed")
    if p.get("execution_authority")!="none" or r.get("status")!="accepted_by_human" or r.get("execution_authority")!="none": return blocked("human_acceptance_required")
    if r.get("proposal_sha256")!=sha(canon(p)): return blocked("proposal_hash_mismatch")
    if not isinstance(r.get("audit_record_sha256"),str) or len(r["audit_record_sha256"])!=64: return blocked("audit_hash_required")
    with inp.open(encoding="utf-8",newline="") as h:
        reader=csv.DictReader(h); fields=reader.fieldnames or []
        if p["column"] not in fields: return blocked("target_column_missing")
        rows=list(reader)
    before=[dict(x) for x in rows]; changed=0
    for row in rows:
        old=row[p["column"]]
        if not isinstance(old,str): return blocked("target_cell_not_text")
        new=old.replace("\t"," ")
        changed += new!=old; row[p["column"]]=new
    out.parent.mkdir(parents=True,exist_ok=True)
    with out.open("x",encoding="utf-8",newline="") as h:
        w=csv.DictWriter(h,fieldnames=fields); w.writeheader(); w.writerows(rows)
    non_target=[n for n in fields if n!=p["column"] and any(before[i][n]!=rows[i][n] for i in range(len(rows)))]
    if non_target or len(rows)!=len(before): out.unlink(missing_ok=True); return blocked("invariant_failure")
    return {"status":"tabs_to_space_executed_safe_file","operation":p["operation"],"target_column":p["column"],"changed_cell_count":changed,"row_count_before":len(before),"row_count_after":len(rows),"columns_before":fields,"columns_after":fields,"non_target_columns_changed":non_target,"input_sha256":sha(inp.read_bytes()),"output_sha256":sha(out.read_bytes()),"execution_timestamp_utc":datetime.now(timezone.utc).isoformat().replace("+00:00","Z"),"source_modified":False,"model_execution_authority":"none","network_request":False,"execution_started":True,"output_path":str(out)}
def main(): print(json.dumps(execute(json.loads(sys.stdin.read())),ensure_ascii=False,sort_keys=True,separators=(",",":")))
if __name__=="__main__": main()

