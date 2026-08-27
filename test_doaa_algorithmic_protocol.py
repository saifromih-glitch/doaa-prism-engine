import copy
from doaa_algorithmic_protocol import encode_request, render_result, validate_result


def request():
    return {
        "protocol": "doaa.alg.v1", "request_id": "req-001",
        "algorithm": {"id": "answer.summarize.v1", "version": "1"},
        "parameters": {"language": "ar", "max_words": 120},
        "context": {"algorithm_refs": [], "user_constraints": ["مباشر"]},
        "input": {"kind": "text", "value": "مادة اختبارية"},
        "output_policy": {"format": "natural_language", "language": "ar"},
        "authority": "none", "automatic_execution": False,
    }


def result_for(req):
    return {"protocol": "doaa.alg.v1", "request_id": req["request_id"],
            "algorithm": req["algorithm"], "status": "completed",
            "result": "ملخص اختباري", "evidence_refs": ["ev-001"],
            "authority": "none", "automatic_execution": False}


def main():
    good = request()
    encoded = encode_request(good)
    assert encoded["status"] == "algorithm_message_valid" and encoded["message"] == good
    for key, value, reason in [("algorithm", {"id": "unknown.v1", "version": "1"}, "algorithm_not_registered"), ("authority", "execute", "authority_invalid"), ("automatic_execution", True, "authority_invalid")]:
        bad = copy.deepcopy(good); bad[key] = value
        assert encode_request(bad)["reason"] == reason
    bad_nested = copy.deepcopy(good); bad_nested["context"]["user_constraints"] = [{"shell": "delete"}]
    assert encode_request(bad_nested)["reason"] == "forbidden_key_detected"
    valid_result = validate_result(result_for(good), good)
    assert valid_result["status"] == "algorithm_result_valid"
    rendered = render_result(valid_result)
    assert rendered["status"] == "natural_language_rendered" and rendered["text"] == "ملخص اختباري"
    bad_result = result_for(good); bad_result["request_id"] = "req-999"
    assert validate_result(bad_result, good)["reason"] == "result_binding_mismatch"
    bad_result = result_for(good); bad_result["tool_call"] = {}
    assert validate_result(bad_result, good)["reason"] == "forbidden_key_detected"
    print('{"tests":8,"status":"passed","authority":"none","automatic_execution":false}')


if __name__ == "__main__":
    main()
