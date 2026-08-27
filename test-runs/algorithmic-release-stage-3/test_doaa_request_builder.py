from doaa_natural_algorithm_proposer import propose
from doaa_request_builder import build


def main():
    proposal = propose("لخص النص بالعربية")
    built = build(proposal, "هذا نص للاختبار", "req-build-1")
    assert built["status"] == "algorithm_request_built"
    assert built["message"]["algorithm"]["id"] == "answer.summarize.v1"
    assert built["message"]["input"]["value"] == "هذا نص للاختبار"
    unknown = propose("لخص الملف وأرسله")
    assert build(unknown, "نص", "req-build-2")["reason"] == "validated_proposal_required"
    assert build(proposal, "", "req-build-3")["reason"] == "text_required"
    bad = dict(proposal); bad["algorithm"] = {"id": "unknown.v1", "version": "1"}
    assert build(bad, "نص", "req-build-4")["reason"] == "algorithm_not_registered"
    print('{"tests":4,"status":"passed","natural_to_algorithm":"validated_only","authority":"none"}')


if __name__ == "__main__":
    main()
