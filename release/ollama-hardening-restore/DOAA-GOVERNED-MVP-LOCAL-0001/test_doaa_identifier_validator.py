import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from doaa_identifier_validator import validate_identifiers
assert validate_identifiers("q1","a1","r1")["status"] == "identifier_verified"
assert validate_identifiers("","a1","r1")["status"] == "identifier_blocked"
assert validate_identifiers("q 1","a1","r1")["status"] == "identifier_blocked"
assert validate_identifiers("q/1","a1","r1")["status"] == "identifier_blocked"
assert validate_identifiers("x"*97,"a1","r1")["status"] == "identifier_blocked"
print(json.dumps({"tests":5,"status":"passed","bounded":True,"automatic_execution":False}, ensure_ascii=False))
