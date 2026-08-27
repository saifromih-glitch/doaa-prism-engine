import hashlib
import json
import subprocess
import inspect
import doaa_excel_safe_execute as executor
import sys
from pathlib import Path
root = Path(__file__).parent
script = root / "doaa_excel_safe_execute.py"
test_root = root / "test-runs-excel"
input_path = test_root / "input-arabic-phone.xlsx"
output_path = test_root / "debug-output.xlsx"
output_path.unlink(missing_ok=True)
proposal = {"kind":"proposal","execution_authority":"none","operation":"remove_ascii_phone_separators","column":"الهاتف","arguments":{},"rationale":"safe"}
canon = json.dumps(proposal, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
review = {"status":"accepted_by_human","execution_authority":"none","proposal_sha256":hashlib.sha256(canon.encode()).hexdigest(),"audit_record_sha256":"d"*64}
payload = {"proposal":proposal,"human_review":review,"input_path":str(input_path),"output_path":str(output_path),"allowed_root":str(test_root),"worksheet":"البيانات"}
print(repr(proposal), repr(proposal.get("operation")), repr(proposal.get("column")), repr(proposal.get("arguments")))
print(proposal.get("operation") != "remove_ascii_phone_separators", proposal.get("column") not in {"phone", "الهاتف"}, proposal.get("arguments") != {})
roundtrip = json.loads(json.dumps(payload, ensure_ascii=False))
print("ROUNDTRIP", repr(roundtrip["proposal"]), roundtrip["proposal"].get("operation") != "remove_ascii_phone_separators", roundtrip["proposal"].get("column") not in {"phone", "الهاتف"}, roundtrip["proposal"].get("arguments") != {})
print("SOURCE", inspect.getsource(executor.execute).splitlines()[5:9])
p = subprocess.run([sys.executable, str(script)], input=json.dumps(payload, ensure_ascii=False), text=True, encoding="utf-8", capture_output=True)
print("returncode", p.returncode)
print("stdout", p.stdout)
print("stderr", p.stderr)
