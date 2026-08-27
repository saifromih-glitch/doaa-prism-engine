import copy
from doaa_algorithmic_mediator import mediate


def req():
    return {
        "protocol": "doaa.alg.v1", "request_id": "req-med-1",
        "algorithm": {"id": "answer.compose.v1", "version": "1"},
        "parameters": {"language": "ar"},
        "context": {"algorithm_refs": [], "user_constraints": []},
        "input": {"kind": "text", "value": "اكتب إجابة قصيرة"},
        "output_policy": {"format": "natural_language", "language": "ar"},
        "authority": "none", "automatic_execution": False,
    }


def result(r):
    return {"protocol": "doaa.alg.v1", "request_id": r["request_id"], "algorithm": r["algorithm"], "status": "completed", "result": "إجابة محكومة", "authority": "none", "automatic_execution": False}


def main():
    r = req()
    ok = mediate(r, result(r))
    assert ok["status"] == "mediation_completed"
    assert ok["model_result_trusted"] is False
    assert ok["rendered"]["text"] == "إجابة محكومة"

    bad_request = copy.deepcopy(r); bad_request["authority"] = "execute"
    blocked = mediate(bad_request, result(r))
    assert blocked["status"] == "mediation_blocked" and blocked["stage"] == "request"

    bad_result = result(r); bad_result["request_id"] = "other"
    blocked = mediate(r, bad_result)
    assert blocked["status"] == "mediation_blocked" and blocked["stage"] == "result"

    bad_result = result(r); bad_result["generated_code"] = "print(1)"
    blocked = mediate(r, bad_result)
    assert blocked["status"] == "mediation_blocked" and blocked["stage"] == "result"
    print('{"tests":4,"status":"passed","model_result_trusted":false,"authority":"none"}')


if __name__ == "__main__":
    main()
