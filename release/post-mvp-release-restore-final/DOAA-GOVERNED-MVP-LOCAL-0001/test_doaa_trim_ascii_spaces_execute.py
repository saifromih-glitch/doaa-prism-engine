import hashlib
import json
import tempfile
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent))
import doaa_trim_ascii_spaces_execute as mod


def canon(v):
    return json.dumps(v, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def main():
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp)
        inp = root / "input.csv"
        out = root / "output.csv"
        inp.write_text("name,phone\n  علي  , 010-20  \nسارة, 011\n", encoding="utf-8", newline="")
        proposal = {"kind":"proposal","operation":"trim_ascii_spaces","column":"name","arguments":{},"execution_authority":"none"}
        review = {"status":"accepted_by_human","execution_authority":"none","proposal_sha256":hashlib.sha256(canon(proposal).encode()).hexdigest(),"audit_record_sha256":"a"*64}
        result = mod.execute({"input_path":str(inp),"output_path":str(out),"allowed_root":str(root),"proposal":proposal,"human_review":review})
        assert result["status"] == "trim_ascii_spaces_executed_safe_file"
        assert result["changed_cell_count"] == 1
        assert out.read_text(encoding="utf-8") == "name,phone\nعلي, 010-20  \nسارة, 011\n"
        blocked = mod.execute({"input_path":str(inp),"output_path":str(root/"blocked.csv"),"allowed_root":str(root),"proposal":proposal,"human_review":{}})
        assert blocked["reason"] == "human_acceptance_required"
    print(json.dumps({"tests":2,"status":"passed","only_target_column_changed":True,"automatic_execution":False}, ensure_ascii=False))


if __name__ == "__main__":
    main()
