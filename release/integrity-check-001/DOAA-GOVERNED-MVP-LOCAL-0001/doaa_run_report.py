import json
def build(result):
    if not isinstance(result, dict):
        return {"status":"run_report_blocked","reason":"result_object_required","execution_authority":"none"}
    status=result.get("status","unknown")
    if status in {"executed_safe_file","excel_executed_safe_file","space_normalize_executed_safe_file","trim_ascii_spaces_executed_safe_file","tabs_to_space_executed_safe_file"}: summary="تم التنفيذ الآمن بعد المراجعة البشرية"
    elif "blocked" in status or result.get("blocked_at"): summary="تم حجب الطلب بأمان"
    else: summary="الطلب في مرحلة المراجعة أو الاقتراح"
    return {"status":"run_report_ready","summary_ar":summary,"result_status":status,"execution_started":bool(result.get("execution_started",False)),"execution_authority":"none","automatic_execution":False,"source_modified":False}
if __name__=="__main__": print(json.dumps(build(json.loads(input())),ensure_ascii=False))
