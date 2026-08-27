import json
import sys
from pathlib import Path

from doaa_security_diagnostics import diagnose
from doaa_safe_file_execute import execute as execute_csv
from doaa_excel_safe_execute import execute as execute_xlsx
from doaa_space_normalize_execute import execute as execute_space_normalize
from doaa_trim_ascii_spaces_execute import execute as execute_trim_ascii_spaces
from doaa_tabs_to_space_execute import execute as execute_tabs_to_space


def main():
    payload = json.loads(sys.stdin.read())
    root = Path(__file__).parent
    diagnostics = diagnose(root)
    if diagnostics["status"] != "diagnostics_passed":
        print(json.dumps({"status":"local_flow_blocked","blocked_at":"diagnostics","diagnostics":diagnostics,"execution_started":False}, ensure_ascii=False, sort_keys=True, separators=(",", ":")))
        return
    suffix = Path(payload.get("input_path", "")).suffix.lower()
    operation = payload.get("proposal", {}).get("operation")
    if operation == "tabs_to_ascii_space":
        result = execute_tabs_to_space(payload)
    elif operation == "trim_ascii_spaces":
        result = execute_trim_ascii_spaces(payload)
    elif operation == "normalize_ascii_spaces":
        result = execute_space_normalize(payload)
    elif suffix == ".csv":
        result = execute_csv(payload)
    elif suffix == ".xlsx":
        result = execute_xlsx(payload)
    else:
        result = {"status":"local_flow_blocked","reason":"unsupported_input_extension","execution_started":False,"model_execution_authority":"none","source_modified":False}
    print(json.dumps({"status":"local_flow_completed" if result.get("status") in {"executed_safe_file","excel_executed_safe_file","space_normalize_executed_safe_file"} else "local_flow_blocked","diagnostics":diagnostics,"execution":result,"execution_started":result.get("execution_started",False)}, ensure_ascii=False, sort_keys=True, separators=(",", ":")))


if __name__ == "__main__":
    main()



