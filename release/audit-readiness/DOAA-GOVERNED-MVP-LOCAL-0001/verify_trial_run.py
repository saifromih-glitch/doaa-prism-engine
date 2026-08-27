import hashlib
import json
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent))
from doaa_run_report import build as build_report

root = Path(__file__).parent / "trial-run-001"
source = root / "input.csv"
reference = root / "input.original.csv"
output = root / "output.csv"
result = json.loads((root / "result.json").read_text(encoding="utf-8"))
source_hash = hashlib.sha256(source.read_bytes()).hexdigest()
reference_hash = hashlib.sha256(reference.read_bytes()).hexdigest()
output_text = output.read_text(encoding="utf-8")
report = build_report(result)
verification = {
    "status": "trial_verified",
    "original_unchanged": source_hash == reference_hash,
    "output_exists": output.is_file(),
    "changed_cell_count": result.get("changed_cell_count"),
    "non_target_columns_changed": result.get("non_target_columns_changed"),
    "execution_authority": result.get("model_execution_authority"),
    "automatic_execution": result.get("automatic_execution", False),
    "report_summary_ar": report.get("summary_ar"),
    "output_utf8_contains_arabic_header": "الهاتف" in output_text,
    "output_phone_values": [line.split(",")[0] for line in output_text.splitlines()[1:]],
}
(root / "trial-verification.json").write_text(json.dumps(verification, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps(verification, ensure_ascii=False))
