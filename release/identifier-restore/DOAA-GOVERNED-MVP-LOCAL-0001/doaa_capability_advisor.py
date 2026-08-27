import json
import re
import sys

SUPPORTED = {"normalize_ascii_spaces", "trim_ascii_spaces", "tabs_to_ascii_space", "remove_ascii_phone_separators"}

def advise(request):
    if not isinstance(request, dict) or set(request) != {"goal"} or not isinstance(request["goal"], str) or not 1 <= len(request["goal"]) <= 2000:
        return {"status":"governed_capability_request","reason":"goal_schema_invalid","execution_authority":"none","automatic_execution":False}
    goal = request["goal"]
    matched = [op for op in SUPPORTED if op in goal]
    if matched:
        return {"status":"known_capability","capability":matched[0],"execution_authority":"none","automatic_execution":False,"requires_normal_flow":True}
    return {"status":"governed_capability_request","goal":goal,"evidence_required":["precise_input_contract","precise_output_contract","threat_model","acceptance_tests","human_review_policy"],"proposed_next_stage":"separate_reviewed_design","prohibited_actions":["modify_source","create_code","execute_commands","install_dependencies","network_request","self_publish"],"execution_authority":"none","automatic_execution":False}

def main():
    print(json.dumps(advise(json.loads(sys.stdin.read())),ensure_ascii=False,sort_keys=True,separators=(",",":")))

if __name__ == "__main__": main()
