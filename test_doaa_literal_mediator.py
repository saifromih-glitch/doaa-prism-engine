import json
from doaa_algorithmic_mediator import mediate

base = {
    "protocol": "doaa.alg.v1",
    "request_id": "literal-test-1",
    "algorithm": {"id": "task.plan.v1", "version": "1"},
    "parameters": {},
    "context": {"algorithm_refs": ["task.plan.v1"], "user_constraints": [], "literal_policy": {"mode": "literal_only", "required_literals": ["الإنسان"]}},
    "input": {"kind": "text", "value": "يجب أن يراجع الإنسان النتيجة."},
    "output_policy": {"format": "natural_language", "language": "ar"},
    "authority": "none",
    "automatic_execution": False,
}

def result(text):
    return {"protocol":"doaa.alg.v1","request_id":"literal-test-1","algorithm":{"id":"task.plan.v1","version":"1"},"status":"completed","authority":"none","automatic_execution":False,"result":text}

passed = mediate(base, result("يجب أن يراجع الإنسان النتيجة."))
blocked = mediate(base, result("يجب أن يراجع النظام النتيجة."))
assert passed["status"] == "mediation_completed", passed
assert blocked["status"] == "mediation_blocked", blocked
assert blocked["stage"] == "literal_compliance", blocked
print(json.dumps({"tests":2,"status":"passed","pass_path":passed["status"],"block_path":blocked["stage"],"execution_authority":"none"}, ensure_ascii=False))
