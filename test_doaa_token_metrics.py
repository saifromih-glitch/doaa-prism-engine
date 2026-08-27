import json
from doaa_token_metrics import compare, estimate_units, measure


def main():
    assert estimate_units("اكتب إجابة قصيرة") > 0
    msg = {"protocol": "doaa.alg.v1", "algorithm": {"id": "answer.summarize.v1", "version": "1"}, "parameters": {"language": "ar"}}
    result = compare("لخص النص التالي بالعربية في إجابة قصيرة ومباشرة مع الحفاظ على المعنى", msg)
    assert result["status"] == "metrics_computed"
    assert result["is_model_usage"] is False
    assert result["natural"]["source"] == "natural_prompt"
    assert result["algorithmic"]["source"] == "algorithm_message"
    assert result["algorithmic"]["utf8_bytes"] == len(json.dumps(msg, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8"))
    try:
        measure("x", "unknown")
    except ValueError as exc:
        assert str(exc) == "source_invalid"
    else:
        raise AssertionError("invalid source accepted")
    print('{"tests":4,"status":"passed","model_usage":false,"estimator":"unicode_word_punctuation_proxy"}')


if __name__ == "__main__":
    main()
