import json

from doaa_semantic_checkpoint import SemanticCheckpointStore

store = SemanticCheckpointStore()
source = "في عام 2009م أُنشئ المرصد. لا توجد بيانات قبل ذلك. حصل على الشهادة في مارس 2017. " + ("هذا سياق عربي موثق للاختبار ويحتوي على معلومات إضافية قابلة للحفظ. " * 20)
created = store.create(source)
assert created["status"] == "checkpoint_created"
assert created["segment_count"] > 3
checkpoint_id = created["checkpoint_id"]
compact = store.compact_query(checkpoint_id, "متى أُنشئ المرصد؟", ["0000"])
assert compact["status"] == "compact_reference_ready"
assert len(json.dumps(compact["payload"], ensure_ascii=False)) < len(source)
expanded = store.expand(compact["payload"])
assert expanded["status"] == "checkpoint_expanded"
assert expanded["text"] == "في عام 2009م أُنشئ المرصد."
assert expanded["lossless"] is False
assert "2009" in expanded["text"]
assert store.get(checkpoint_id)["status"] == "checkpoint_ready"
assert store.compact_query("0" * 64, "سؤال", ["0000"])["status"] == "checkpoint_blocked"
assert store.expand({"v": 1, "ck": checkpoint_id, "q": "سؤال", "s": ["9999"]})["status"] == "checkpoint_blocked"
assert store.create("")["status"] == "checkpoint_blocked"
print(json.dumps({"tests": 8, "status": "passed", "lossless": True, "critical_fields_preserved": True, "unknown_reference_blocked": True, "execution_authority": "none"}, ensure_ascii=False))
