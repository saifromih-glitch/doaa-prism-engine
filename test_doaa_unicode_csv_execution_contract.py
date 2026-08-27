import json
from pathlib import Path

contract = json.loads((Path(__file__).parent / "CONTRACT-DSL-UNICODE-CSV-EXECUTION-0001.json").read_text(encoding="utf-8"))
assert contract["operation"] == "normalize_unicode_whitespace"
assert contract["format"] == "CSV"
assert contract["allowed_codepoints"] == ["U+00A0", "U+202F"]
assert contract["replacement"] == "U+0020"
assert contract["preview_hash_required"] is True
assert contract["human_review_required"] is True
assert contract["execution_authority"] == "none"
assert contract["automatic_execution"] is False
assert contract["overwrite_input"] is False
assert contract["source_modification"] is False
assert set(contract["invariants"]) == {"row_count_unchanged", "column_set_unchanged", "non_target_columns_unchanged", "only_allowed_codepoints_replaced"}
print(json.dumps({"tests":10,"status":"passed","unicode_csv_contract":"bounded","allowed_codepoints":["U+00A0","U+202F"],"execution_authority":"none"}, ensure_ascii=False))
