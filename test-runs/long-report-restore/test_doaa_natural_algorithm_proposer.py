from doaa_natural_algorithm_proposer import propose


def main():
    ok = propose("لخص النص بالعربية")
    assert ok["status"] == "algorithmic_classification_proposal"
    assert ok["algorithm"]["id"] == "answer.summarize.v1"
    assert ok["requires_validation"] is True and ok["requires_review"] is True
    assert ok["execution_authority"] == "none" and ok["automatic_execution"] is False
    ok = propose("  plan task  ")
    assert ok["status"] == "algorithmic_classification_proposal"
    assert ok["algorithm"]["id"] == "task.plan.v1"
    unknown = propose("لخص هذا الملف ثم أرسله بالبريد")
    assert unknown["status"] == "governed_capability_request"
    empty = propose("")
    assert empty["reason"] == "text_required"
    bad_language = propose("لخص النص", "fr")
    assert bad_language["reason"] == "language_unsupported"
    print('{"tests":5,"status":"passed","proposal_only":true,"authority":"none"}')


if __name__ == "__main__":
    main()
