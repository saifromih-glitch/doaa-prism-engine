import sys
sys.path.insert(0, r"C:\Users\saifr\OneDrive\Desktop\Doaa-Local")
from doaa_final_audit_completeness import verify_final_audit
required=["proposal","gate","human_review","approval","execution_receipt","manifest_binding"]
good={k:{"verified":True} for k in required}
cases=[("good",good,"final_audit_verified"),("missing",{k:v for k,v in good.items() if k!="gate"},"final_audit_blocked"),("sensitive",{**good,"proposal":{"verified":True,"token":"x"}},"final_audit_blocked"),("unverified",{**good,"approval":{"verified":False}},"final_audit_blocked")]
for name,payload,expected in cases:
    result=verify_final_audit(payload)
    assert result["status"]==expected,(name,result)
    assert result["automatic_execution"] is False
print({"tests":len(cases),"status":"passed"})
