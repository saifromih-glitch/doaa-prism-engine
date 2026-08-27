import hashlib,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent))
from doaa_daily_ui import build_request
from doaa_preview import preview
from doaa_trim_ascii_spaces_execute import execute
root=Path(__file__).parent/"full-ui-trial-001"; root.mkdir(exist_ok=True)
inp=root/"input.csv"; out=root/"output.csv"
out.unlink(missing_ok=True)
inp=root/"input.csv"; out=root/"output.csv"
inp.write_text("الهاتف,الاسم,المبلغ\n 010-123 ,عميل دورة,100\n",encoding="utf-8")
request=build_request(str(inp),str(out),"trim_ascii_spaces","الهاتف")
pre=preview(request)
assert pre["status"]=="preview_ready" and pre["changed_cell_count"]==1 and not out.exists()
proposal=request["proposal"]; canonical=json.dumps(proposal,ensure_ascii=False,sort_keys=True,separators=(",",":"))
request["human_review"]={"status":"accepted_by_human","execution_authority":"none","proposal_sha256":hashlib.sha256(canonical.encode()).hexdigest(),"audit_record_sha256":"b"*64}
result=execute(request)
assert result["status"]=="trim_ascii_spaces_executed_safe_file" and result["execution_started"] is True and result["source_modified"] is False
assert out.exists()
print(json.dumps({"status":"full_ui_flow_passed","preview_changed":pre["changed_cell_count"],"human_review":"accepted_by_human","execution_started":result["execution_started"],"source_modified":result["source_modified"],"output_exists":out.exists()},ensure_ascii=False))


