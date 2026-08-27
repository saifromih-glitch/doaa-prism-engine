import json

BLOCK_REASON_AR = {
    "proposal_hash_mismatch": "لم يتطابق الطلب مع الاقتراح المعتمد؛ أعد المعاينة قبل الموافقة.",
    "audit_hash_required": "تعذر التحقق من سجل التدقيق؛ لا يمكن التنفيذ.",
    "human_acceptance_required": "يلزم قبول بشري صريح قبل التنفيذ.",
    "source_modified": "تغير الملف منذ المعاينة؛ أعد المعاينة والموافقة.",
    "worksheet_not_unique": "تعذر تحديد ورقة العمل المطلوبة بشكل فريد.",
    "target_column_missing": "العمود المطلوب غير موجود في ورقة العمل.",
    "input_read_failure": "تعذر قراءة الملف؛ تحقق من المسار والترميز وصحة الملف.",
    "invalid_contract": "بيانات الطلب غير مكتملة أو غير صالحة.",
    "output_policy_violation": "مسار الإخراج غير مسموح أو الملف موجود مسبقًا.",
}


def build(result):
    if not isinstance(result, dict):
        return {"status": "run_report_blocked", "reason": "result_object_required", "reason_ar": "بيانات النتيجة غير صالحة.", "execution_authority": "none"}
    status = result.get("status", "unknown")
    blocked = "blocked" in status or bool(result.get("blocked_at"))
    if status in {"executed_safe_file", "excel_executed_safe_file", "space_normalize_executed_safe_file", "trim_ascii_spaces_executed_safe_file", "tabs_to_space_executed_safe_file"}:
        summary = "تم التنفيذ الآمن بعد المراجعة البشرية"
    elif blocked:
        summary = "تم حجب الطلب بأمان"
    else:
        summary = "الطلب في مرحلة المراجعة أو الاقتراح"
    reason = result.get("reason")
    reason_ar = BLOCK_REASON_AR.get(reason, "تعذر إكمال الطلب بأمان.") if blocked else ""
    return {"status": "run_report_ready", "summary_ar": summary, "reason": reason, "reason_ar": reason_ar, "result_status": status, "execution_started": bool(result.get("execution_started", False)), "execution_authority": "none", "automatic_execution": False, "source_modified": False}


if __name__ == "__main__":
    print(json.dumps(build(json.loads(input())), ensure_ascii=False))
