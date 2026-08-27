import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from doaa_proposal_gate import validate_model_output

request = {"goal": "تنظيف عمود الاسم", "table_schema": [{"name": "name", "type": "text"}, {"name": "phone", "type": "text"}], "dsl_version": "1.4"}
base = {"kind": "proposal", "execution_authority": "none", "operation": "remove_ascii_phone_separators", "column": "phone", "arguments": {}, "rationale": "تنظيف محدود"}
for operation, column in (("remove_ascii_phone_separators", "phone"), ("normalize_ascii_spaces", "name"), ("trim_ascii_spaces", "name"), ("tabs_to_ascii_space", "name")):
    accepted = validate_model_output(dict(base, operation=operation, column=column), request)
    assert accepted["status"] == "accepted_proposal" and accepted["execution_authority"] == "none"
unknown = dict(base, operation="invented_operation")
assert validate_model_output(unknown, request)["reason"] == "operation_not_registered"
unicode_proposal = dict(base, operation="normalize_unicode_whitespace", column="name")
unicode_accept = validate_model_output(unicode_proposal, request)
assert unicode_accept["status"] == "accepted_proposal" and unicode_accept["execution_authority"] == "none"
missing_column = dict(base, column="amount")
assert validate_model_output(missing_column, request)["reason"] == "column_not_declared_text"
for key, value in (("shell_command", "del *"), ("generated_code", "print(1)"), ("network_instruction", "https://example.com")):
    executable = dict(base)
    executable[key] = value
    result = validate_model_output(executable, request)
    assert result["status"] == "rejected" and result["execution_authority"] == "none"
assert validate_model_output({"kind":"proposal","execution_authority":"execute","operation":"remove_ascii_phone_separators","column":"phone","arguments":{},"rationale":"x"}, request)["reason"] == "execution_authority_not_none"
print(json.dumps({"tests":11,"status":"passed","unknown_operation_rejected":True,"unknown_column_rejected":True,"executable_content_rejected":True,"execution_authority":"none"}, ensure_ascii=False))
