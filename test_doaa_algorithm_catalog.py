from doaa_algorithm_catalog import CATALOG, list_registered, lookup, propose_new_algorithm


def main():
    before = list_registered()
    hit = lookup("answer.summarize.v1", "1")
    assert hit["status"] == "catalog_hit"
    assert hit["execution_authority"] == "none" and hit["automatic_execution"] is False
    miss = lookup("answer.summarize.v1", "2")
    assert miss["status"] == "catalog_miss"
    miss = lookup("unknown.algorithm.v1", "1")
    assert miss["status"] == "catalog_miss"
    proposal = propose_new_algorithm({"id": "answer.translate.v1", "purpose": "translate"})
    assert proposal["status"] == "governed_capability_request"
    assert list_registered() == before
    assert len(CATALOG) == 3
    print('{"tests":5,"status":"passed","catalog_mutated":false,"authority":"none"}')


if __name__ == "__main__":
    main()
