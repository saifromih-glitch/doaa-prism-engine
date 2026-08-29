import tempfile
from pathlib import Path
from doaa_efficiency_router import choose_route
from doaa_route_cache import RouteCache, cache_key


def test_snippet_route_for_long_context():
    context = "تأسست الشركة عام 2010. بلغت الإيرادات 25 مليون جنيه في عام 2024. يقع المقر في القاهرة."
    result = choose_route("ما قيمة الإيرادات في عام 2024؟", context)
    assert result["route"] in {"evidence_snippet", "warm_checkpoint"}
    assert result["safe"] is True


def test_fallback_for_unrelated_question():
    result = choose_route("من هو مؤلف الكتاب؟", "بلغت الإيرادات 25 مليون جنيه في عام 2024.")
    assert result["route"] == "baseline_or_review"
    assert result["safe"] is False


def test_cache_key_is_stable_and_scoped():
    context, question = "نص عربي", "سؤال عربي"
    assert cache_key(context, question) == cache_key(context, question)
    assert cache_key(context, question) != cache_key(context + " مختلف", question)


def test_cache_hit():
    with tempfile.TemporaryDirectory() as d:
        cache = RouteCache(str(Path(d) / "cache.json"))
        cache.put("سياق", "سؤال", {"answer": "نتيجة"})
        result = choose_route("سؤال", "سياق", cache=cache)
        assert result["route"] == "local_exact"


if __name__ == "__main__":
    test_snippet_route_for_long_context()
    test_fallback_for_unrelated_question()
    test_cache_key_is_stable_and_scoped()
    test_cache_hit()
    print("ok")
