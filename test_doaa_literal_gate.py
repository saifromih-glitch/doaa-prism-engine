import json
from doaa_literal_gate import check


def request(policy):
    return {"context": {"literal_policy": policy}, "input": {"value": "الإجمالي 100 ملف، والرقمية 40 ملفًا."}}

assert check(request({"mode": "literal_only"}), "40 ملفًا من أصل 100.")["passed"] is True
assert check(request({"mode": "literal_only"}), "النسبة 50% من أصل 100.")["passed"] is False
assert check(request({"mode": "literal_only", "required_literals": ["40"]}), "الإجمالي 100 فقط.")["passed"] is False
assert check(request({"mode": "literal_only", "forbidden_patterns": ["أرسل"]}), "أرسل التقرير")["passed"] is False
assert check(request({"mode": "literal_only", "exact_sentence_count": 2}), "الأول. الثاني.")["passed"] is True
print(json.dumps({"tests": 5, "status": "passed", "fail_closed": True, "execution_authority": "none"}, ensure_ascii=False))
