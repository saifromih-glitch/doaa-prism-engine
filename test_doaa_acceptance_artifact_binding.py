import json
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent))
from doaa_artifact_release_consistency import verify_consistency

root = Path(__file__).parent
artifact = json.loads((root / "DOAA-STATIC-BOUNDARY-ACCEPTANCE-0001.json").read_text(encoding="utf-8-sig"))
manifest = json.loads((root / "DOAA-GOVERNED-MVP-0001-manifest.json").read_text(encoding="utf-8-sig"))
release_id = manifest["release_id"]
manifest_hash = manifest["manifest_sha256"]
bound_artifact = {**artifact, "manifest_sha256": manifest_hash}
assert verify_consistency(bound_artifact, release_id, manifest_hash)["status"] == "consistency_verified"
assert verify_consistency({**artifact, "release_id": "OTHER-RELEASE"}, release_id, manifest_hash)["reason"] == "release_id_mismatch"
assert verify_consistency({**artifact, "manifest_sha256": "0" * 64}, release_id, manifest_hash)["reason"] == "manifest_hash_mismatch"
print({"tests":3,"status":"passed","release_bound":True,"automatic_execution":False,"execution_authority":"none"})
