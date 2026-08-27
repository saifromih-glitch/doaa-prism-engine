import hashlib
import json
import tempfile
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
import sys
sys.path.insert(0, str(Path(__file__).parent))
from doaa_zip_manifest_verifier import verify_package

with tempfile.TemporaryDirectory() as temp:
    root = Path(temp)
    source = root / "sample.txt"
    data = b"governed"
    source.write_bytes(data)
    manifest = {"files": [{"path": "sample.txt", "sha256": hashlib.sha256(data).hexdigest()}]}
    manifest_path = root / "manifest.json"
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    package = root / "package.zip"
    with ZipFile(package, "w", ZIP_DEFLATED) as archive:
        archive.writestr("pkg/sample.txt", data)
    result = verify_package(root, manifest_path, package)
    assert result["status"] == "package_consistency_verified", result
    assert result["files_verified"] == 1
    assert result["read_only"] is True
    assert result["automatic_execution"] is False
print({"tests":4,"status":"passed","files_verified":1,"read_only":True,"automatic_execution":False})
