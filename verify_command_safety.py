import ast
import json
from pathlib import Path

source = Path("doaa_command_language.py").read_text(encoding="utf-8")
tree = ast.parse(source)
forbidden = {"os", "subprocess", "socket", "open", "Path", "exec", "eval", "requests", "urllib", "http"}
found = []
for node in ast.walk(tree):
    if isinstance(node, (ast.Import, ast.ImportFrom)):
        names = [alias.name.split(".")[0] for alias in node.names]
        found.extend(name for name in names if name in forbidden)
    elif isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id in forbidden:
        found.append(node.func.id)
assert not found, found
print(json.dumps({"status": "passed", "forbidden_apis": [], "module": "doaa_command_language.py"}))
