from doaa_distillation import propose_distillation


def record(algorithm_id="answer.summarize.v1"):
    return {"status": "accepted", "algorithm": {"id": algorithm_id, "version": "1"}, "execution_authority": "none", "automatic_execution": False}


def main():
    records = [record(), record(), record()]
    ok = propose_distillation(records)
    assert ok["status"] == "distillation_candidate"
    assert ok["candidate"]["support"] == 3
    assert ok["candidate"]["required_review"] is True
    assert ok["candidate"]["library_mutation"] is False
    assert ok["candidate"]["model_update"] is False
    assert propose_distillation([record(), record()])["reason"] == "insufficient_support"
    bad = record(); bad["status"] = "proposed"
    assert propose_distillation([record(), record(), bad])["reason"] == "unaccepted_record_present"
    bad = record(); bad["shell"] = "rm -rf"
    assert propose_distillation([record(), record(), bad])["reason"] == "unaccepted_record_present"
    assert propose_distillation(records, 1)["reason"] == "input_invalid"
    print('{"tests":5,"status":"passed","library_mutation":false,"model_update":false,"authority":"none"}')


if __name__ == "__main__":
    main()
