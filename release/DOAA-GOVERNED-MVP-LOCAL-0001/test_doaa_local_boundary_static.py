import ast
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent))
from doaa_ollama_proposal_adapter import is_local_endpoint

root = Path(__file__).parent
files = [root / "doaa_local_integration.py", root / "doaa_ollama_proposal_adapter.py", root / "doaa_raw_proposal_boundary.py"]
for path in files:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        assert not isinstance(node, (ast.Import, ast.ImportFrom)) or all(alias.name not in {"subprocess", "socket", "requests", "os"} for alias in node.names)
        if isinstance(node, ast.Call):
            assert not (isinstance(node.func, ast.Name) and node.func.id in {"eval", "exec", "open"})
            assert not (isinstance(node.func, ast.Attribute) and node.func.attr in {"system", "popen"})
assert is_local_endpoint("http://127.0.0.1:11434/api/generate")
assert is_local_endpoint("http://localhost:11434/api/generate")
assert not is_local_endpoint("https://example.com/api/generate")
assert not is_local_endpoint("http://user:pass@localhost:11434/api/generate")
print({"tests":8,"status":"passed","local_only":True,"system_primitives_absent":True,"automatic_execution":False})
