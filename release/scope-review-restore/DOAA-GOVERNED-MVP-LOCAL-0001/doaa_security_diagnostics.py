import hashlib
import json
import shutil
import sys
from pathlib import Path


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def diagnose(root):
    root = Path(root).resolve()
    checks = {}
    failures = []
    required = ["doaa_proposal_gate.py", "doaa_proposal_repair.py", "doaa_audit_log.py", "doaa_human_review.py", "doaa_dsl_dry_run.py", "doaa_safe_file_execute.py", "DOAA-GOVERNED-MVP-0001-manifest.json"]
    checks["project_root_exists"] = root.is_dir()
    checks["required_files_present"] = all((root / name).is_file() for name in required)
    checks["python_version"] = {"major": sys.version_info.major, "minor": sys.version_info.minor, "supported": sys.version_info >= (3, 11)}
    checks["ollama_discovery_only"] = {"present": shutil.which("ollama.exe") is not None, "model_execution": False}
    manifest_path = root / "DOAA-GOVERNED-MVP-0001-manifest.json"
    checks["manifest_verified"] = False
    if manifest_path.is_file():
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        file_results = []
        for entry in manifest.get("files", []):
            path = root / entry["path"]
            ok = path.is_file() and sha256(path) == entry["sha256"] and path.stat().st_size == entry["size"]
            file_results.append({"path": entry["path"], "verified": ok})
        checks["manifest_files"] = file_results
        checks["manifest_verified"] = all(item["verified"] for item in file_results)
    checks["network_request"] = False
    checks["source_modified"] = False
    checks["real_data_used"] = False
    checks["execution_started"] = False
    required_true = ["project_root_exists", "required_files_present", "manifest_verified"]
    failures.extend(name for name in required_true if checks.get(name) is not True)
    if checks["python_version"].get("supported") is not True:
        failures.append("python_version")
    return {"status": "diagnostics_passed" if not failures else "diagnostics_failed", "contract_id": "CONTRACT-SECURITY-DIAGNOSTICS-0001", "checks": checks, "failures": failures, "model_execution_authority": "none"}


def main():
    root = sys.argv[1] if len(sys.argv) > 1 else str(Path(__file__).parent)
    print(json.dumps(diagnose(root), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
