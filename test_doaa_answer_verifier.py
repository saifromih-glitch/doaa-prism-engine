import json

from doaa_answer_verifier import verify_answer

context = "يترأس مجلس المرصد أمير المنطقة بالإضافة إلى أربعة عشر عضوا، وإنشاء المرصد في عام 2009م."
assert verify_answer("من يترأس؟", context, "أمير المنطقة")["status"] == "supported"
assert verify_answer("متى؟", context, "عام 2009م")["status"] == "supported"
extra = verify_answer("من يترأس؟", context, "أمير المنطقة في عام 2020")
assert extra["status"] == "unsupported"
assert extra["reason"] == "unseen_numeric_term"
assert "2020" in extra["unsupported_terms"]
assert verify_answer("من؟", context, "")["status"] == "empty"
assert verify_answer("من؟", context, "رئيس الوزراء")["status"] == "unsupported"
assert verify_answer("ما الفائدة؟", "الهدف هو فهم الوضع الحالي للمدينة", "فهم الوضع الحالي للمدينة")["status"] == "supported"
blocked = verify_answer(None, context, "أمير المنطقة")
assert blocked["status"] == "blocked"
forbidden = verify_answer("من؟", context, "أمير المنطقة؛ وتم إطلاق مشروع جديد")["status"]
assert forbidden == "unsupported"
print(json.dumps({"tests": 8, "status": "passed", "extractive": True, "unseen_numeric_block": True, "semantic_truth_claim": False, "execution_authority": "none"}, ensure_ascii=False))
