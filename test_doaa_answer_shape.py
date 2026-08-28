import json
from doaa_answer_shape import build_request, classify_question, parse_json, validate_response

context = "بلغ عدد سكان بورتاج 2,638 نسمة بحسب تعداد عام 2010، وبلغ متوسط حجم الأسرة 2.27."
request = build_request("q-1", "ما هو عدد سكان بورتاج؟", context)
assert classify_question("ما هو عدد سكان بورتاج؟") == "numeric"
assert request["question_type"] == "numeric"
valid = {"question_id": "q-1", "answer": "2,638 نسمة", "evidence_quote": "بلغ عدد سكان بورتاج 2,638 نسمة", "uncertainty": "none", "answer_units": "نسمة"}
assert validate_response(valid, request)["status"] == "supported"
assert validate_response({**valid, "answer": "99,999 نسمة"}, request)["status"] == "fallback_or_review"
assert validate_response({**valid, "evidence_quote": "معلومة غير موجودة"}, request)["status"] == "fallback_or_review"
assert validate_response({**valid, "question_id": "q-2"}, request)["status"] == "fallback_or_review"
assert parse_json(json.dumps(valid, ensure_ascii=False))["question_id"] == "q-1"
print(json.dumps({"tests": 7, "status": "passed", "arabic": True, "exact_evidence_required": True, "execution_authority": "none"}, ensure_ascii=False))
