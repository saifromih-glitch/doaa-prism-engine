import json
import re
import sys

ID = re.compile(r"^[A-Za-z0-9._:-]{1,96}$")
FORBIDDEN = {"command", "shell_command", "source_code", "generated_code", "credentials", "network_instruction", "arbitrary_file_operation", "write_path", "subprocess", "secret_access"}


def classify(message):
    if not isinstance(message, dict) or set(message) != {"message_id", "model_id", "proposal", "execution_authority"}:
        return {"status":"model_mediation_blocked","reason":"envelope_schema_invalid","execution_authority":"none","automatic_execution":False}
    if not ID.fullmatch(message["message_id"]) or not ID.fullmatch(message["model_id"]):
        return {"status":"model_mediation_blocked","reason":"identity_invalid","execution_authority":"none","automatic_execution":False}
    if message["execution_authority"] != "none":
        return {"status":"model_mediation_blocked","reason":"authority_invalid","execution_authority":"none","automatic_execution":False}
    if not isinstance(message["proposal"], dict):
        return {"status":"model_mediation_blocked","reason":"structured_proposal_required","execution_authority":"none","automatic_execution":False}
    bad = sorted(FORBIDDEN.intersection(message["proposal"]))
    if bad:
        return {"status":"model_mediation_blocked","reason":"executable_content_rejected","keys":bad,"execution_authority":"none","automatic_execution":False}
    return {"status":"model_proposal_accepted_for_gate","message_id":message["message_id"],"model_id":message["model_id"],"proposal_keys":sorted(message["proposal"]),"execution_authority":"none","automatic_execution":False,"human_review_required":True,"execution_started":False}


def main():
    print(json.dumps(classify(json.loads(sys.stdin.read())),ensure_ascii=False,sort_keys=True,separators=(",",":")))

if __name__ == "__main__": main()
