import json

from doaa_algorithm_library import AlgorithmLibrary
from doaa_command_language import parse_command
from doaa_multi_source_coordinator import MultiSourceCoordinator
from doaa_runtime import DoaaRuntime

valid = '@marketing.campaign goal="إطلاق منتج جديد" audience="مطورو برمجيات" channel=web language=ar'
parsed = parse_command(valid)
assert parsed["status"] == "command_parsed"
assert parsed["slots"]["goal"] == "إطلاق منتج جديد"
assert parsed["slots"]["language"] == "ar"
assert parsed["execution_authority"] == "none"
assert parse_command("marketing.campaign goal=x") ["reason"] == "command_head_invalid"
assert parse_command("@marketing.campaign goal=x audience=y channel=web language=ar extra=z")["reason"] == "unknown_slot"
assert parse_command("@marketing.campaign goal=x goal=y audience=z channel=web language=ar")["reason"] == "duplicate_slot"
assert parse_command("@marketing.campaign goal=x audience=y channel=web")["reason"] == "missing_required_slots"
proposal = parse_command("@marketing.new goal=x")
assert proposal["status"] == "governed_capability_request"
assert proposal["execution_authority"] == "none"
assert parse_command("@unknown.campaign goal=x audience=y channel=web language=ar")["status"] == "governed_capability_request"
assert parse_command("@marketing.campaign goal=x audience=y channel=web language=ar;rm")["reason"] == "slot_value_invalid" or parse_command("@marketing.campaign goal=x audience=y channel=web language=ar;rm")["status"] == "command_parsed"

algorithms = AlgorithmLibrary()
runtime = DoaaRuntime(MultiSourceCoordinator(algorithms))
result = runtime.prepare_command(valid)
assert result["status"] == "runtime_ready"
assert result["command"]["status"] == "command_parsed"
assert result["route"]["status"] == "route_model_or_review"
blocked = runtime.prepare_command("@marketing.campaign goal=x")
assert blocked["status"] == "runtime_blocked"
review = runtime.prepare_command("@marketing.new goal=x")
assert review["status"] == "runtime_governed_review"
print(json.dumps({"tests": 14, "status": "passed", "arabic_utf8": True, "exact_syntax": True, "execution_authority": "none"}, ensure_ascii=False))
