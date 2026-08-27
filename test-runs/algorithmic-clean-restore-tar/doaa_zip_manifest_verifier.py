import hashlib
from pathlib import Path
from zipfile import ZipFile


def verify_package(root, manifest_path, zip_path):
    root = Path(root)
    manifest_path = Path(manifest_path)
    zip_path = Path(zip_path)
    if not root.is_dir() or not manifest_path.is_file() or not zip_path.is_file():
        return {"status": "package_consistency_blocked", "reason": "package_input_missing", "execution_authority": "none", "automatic_execution": False, "writes_files": False}
    try:
        import json
        manifest = json.loads(manifest_path.read_text(encoding="utf-8-sig"))
        entries = manifest["files"]
        expected = {entry["path"]: entry["sha256"] for entry in entries}
        if len(expected) != len(entries):
            return {"status": "package_consistency_blocked", "reason": "manifest_duplicate_path", "execution_authority": "none", "automatic_execution": False, "writes_files": False}
        with ZipFile(zip_path) as archive:
            names = {name for name in archive.namelist() if not name.endswith("/")}
            prefix = next((name.split("/")[0] for name in archive.namelist() if "/" in name), None)
            if not prefix:
                return {"status": "package_consistency_blocked", "reason": "package_prefix_missing", "execution_authority": "none", "automatic_execution": False, "writes_files": False}
            package_files = {name[len(prefix) + 1:] for name in names if name.startswith(prefix + "/")}
            missing = sorted(set(expected) - package_files)
            extra = sorted(package_files - set(expected) - {"DOAA-GOVERNED-MVP-0001-manifest.json"})
            if missing or extra:
                return {"status": "package_consistency_blocked", "reason": "package_file_set_mismatch", "missing": missing, "extra": extra, "execution_authority": "none", "automatic_execution": False, "writes_files": False}
            for path, digest in expected.items():
                actual = hashlib.sha256(archive.read(prefix + "/" + path)).hexdigest()
                if actual != digest:
                    return {"status": "package_consistency_blocked", "reason": "package_hash_mismatch", "path": path, "execution_authority": "none", "automatic_execution": False, "writes_files": False}
    except (OSError, KeyError, TypeError, ValueError, UnicodeError):
        return {"status": "package_consistency_blocked", "reason": "package_unreadable", "execution_authority": "none", "automatic_execution": False, "writes_files": False}
    return {"status": "package_consistency_verified", "files_verified": len(expected), "execution_authority": "none", "automatic_execution": False, "writes_files": False, "read_only": True}

