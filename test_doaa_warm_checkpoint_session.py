import json

from doaa_warm_checkpoint_session import WarmCheckpointSession

session = WarmCheckpointSession("arabic-benchmark-1")
assert session.prepare_query("سؤال")["status"] == "warm_checkpoint_blocked"
source = "في عام 2009م أُنشئ المرصد. حصل على الشهادة في مارس 2017. " + ("سياق إضافي موثق. " * 10)
registered = session.register_source(source)
assert registered["status"] == "source_registered"
assert registered["source_sent_once"] is True
assert session.register_source(source)["reason"] == "source_already_registered"
query = session.prepare_query("متى أُنشئ المرصد؟")
assert query["status"] == "warm_query_ready"
assert query["source_sent_once"] is False
assert query["request_count"] == 1
expanded = session.expand_for_verification(query["payload"])
assert expanded["status"] == "checkpoint_expanded"
assert expanded["lossless"] is True
assert expanded["text"] == source
assert session.close()["status"] == "warm_session_closed"
assert session.prepare_query("سؤال")["reason"] == "session_closed"
print(json.dumps({"tests": 8, "status": "passed", "source_sent_once": True, "reference_reversible": True, "automatic_execution": False, "execution_authority": "none"}, ensure_ascii=False))
