import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
import doaa_local_integration as m
ok = m.classify({"request_id":"req-1","payload":{"operation":"trim_ascii_spaces"},"execution_authority":"none"})
assert ok["status"] == "integration_message_accepted_for_governed_flow"
xlsx = m.classify({"request_id":"req-xlsx-unicode","payload":{"format":"xlsx","worksheet":"بيانات","operation":"normalize_unicode_whitespace","column":"الاسم","human_review_required":True},"execution_authority":"none"})
assert xlsx["status"] == "integration_message_accepted_for_governed_flow"
bad = m.classify({"request_id":"req-2","payload":{"shell":"dir"},"execution_authority":"none"})
assert bad["status"] == "integration_blocked"
source = m.classify({"request_id":"req-4","payload":{"source_code":"print(1)"},"execution_authority":"none"})
assert source["status"] == "integration_blocked"
path = m.classify({"request_id":"req-5","payload":{"write_path":"out.xlsx"},"execution_authority":"none"})
assert path["status"] == "integration_blocked"
extra = m.classify({"request_id":"req-3","payload":{},"execution_authority":"none","execute":True})
assert extra["status"] == "integration_blocked"
id_bad = m.classify({"request_id":"req/invalid","payload":{},"execution_authority":"none"})
assert id_bad["status"] == "integration_blocked"
authority_bad = m.classify({"request_id":"req-6","payload":{},"execution_authority":"execute"})
assert authority_bad["status"] == "integration_blocked"
payload_bad = m.classify({"request_id":"req-7","payload":[],"execution_authority":"none"})
assert payload_bad["status"] == "integration_blocked"
malformed = m.classify({"request_id":"req-8","payload":{"operation":"normalize_unicode_whitespace"}})
assert malformed["status"] == "integration_blocked"
print(json.dumps({"tests":10,"status":"passed","xlsx_unicode_envelope":True,"commands_rejected":True,"code_rejected":True,"path_write_rejected":True,"invalid_id_rejected":True,"authority_rejected":True,"automatic_execution":False}, ensure_ascii=False))
