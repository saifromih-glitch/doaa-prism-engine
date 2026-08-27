from doaa_compact_reference import encode, reference_definition


def main():
    assert reference_definition("R1")["algorithm_id"] == "answer.summarize.v1"
    ready = encode("R1", "نص متغير", "ar", 3)
    assert ready["status"] == "compact_request_ready"
    assert ready["message"]["r"] == "R1" and ready["message"]["x"] == "نص متغير"
    assert ready["authority"] == "none" and ready["automatic_execution"] is False
    assert encode("R9", "نص")["reason"] == "reference_unknown"
    assert encode("R1", "نص", "fr")["reason"] == "content_or_language_invalid"
    assert encode("R1", "x", "ar", 0)["reason"] == "limit_invalid"
    assert encode("R1", "x" * 9000)["reason"] == "request_too_large"
    print('{"tests":6,"status":"passed","reusable_reference":true,"authority":"none"}')


if __name__ == "__main__":
    main()
