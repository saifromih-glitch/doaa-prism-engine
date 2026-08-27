import json
import sys
from pathlib import Path


def build(registry_path):
    path = Path(registry_path)
    if not path.is_file():
        return {"status":"research_report_blocked","reason":"registry_not_found","execution_authority":"none","automatic_execution":False}
    sources=[]
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            try: sources.append(json.loads(line))
            except json.JSONDecodeError: return {"status":"research_report_blocked","reason":"registry_record_invalid","execution_authority":"none","automatic_execution":False}
    return {"status":"research_report_ready_read_only","source_count":len(sources),"sources":sources,"execution_authority":"none","automatic_execution":False,"execution_started":False,"result_to_execution":"forbidden_without_separate_validation"}


def main():
    print(json.dumps(build(sys.argv[1]),ensure_ascii=False,sort_keys=True,separators=(",",":")))

if __name__ == "__main__": main()
