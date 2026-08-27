import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parent
REPAIR = ROOT / "doaa_proposal_repair.py"
REQUEST = {"goal":"Remove separators from phone only","table_schema":[{"name":"phone","type":"text"},{"name":"amount","type":"number"}],"dsl_version":"1.4"}
PROPOSAL = {"kind":"proposal","execution_authority":"none","operation":"remove_ascii_phone_separators","column":"phone","arguments":{},"rationale":"Narrow text-column transform."}


def run(raw):
    payload = json.dumps({"request":REQUEST,"raw_model_text":raw})
    completed = subprocess.run([sys.executable,str(REPAIR)],input=payload,text=True,encoding="utf-8",capture_output=True,check=True)
    return json.loads(completed.stdout)


def expect(name, result, status, repair_id):
    if result.get("status") != status or result.get("repair_id") != repair_id or result.get("raw_preserved") is not True:
        raise AssertionError((name,result))

expect("plain accepted",run(json.dumps(PROPOSAL)),"accepted_proposal",None)
expect("fenced accepted",run("```json\n"+json.dumps(PROPOSAL)+"\n```"),"accepted_proposal","remove_one_complete_json_code_fence")
expect("semantic mutation rejected",run(json.dumps(dict(PROPOSAL,column="amount"))),"rejected",None)
expect("partial fence rejected",run("```json\n"+json.dumps(PROPOSAL)),"rejected",None)
expect("unknown operation rejected",run(json.dumps(dict(PROPOSAL,operation="invented_operation"))),"rejected",None)
print(json.dumps({"tests":5,"status":"passed","execution_authority":"none","dsl_execution":False},separators=(",",":")))
