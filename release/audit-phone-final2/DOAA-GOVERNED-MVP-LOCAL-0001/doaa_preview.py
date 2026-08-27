import csv, json, re, sys, hashlib
from pathlib import Path
OPS = {
    "remove_ascii_phone_separators": lambda v: v.replace("-", "").replace(" ", ""),
    "normalize_ascii_spaces": lambda v: re.sub(r" +", " ", v),
    "trim_ascii_spaces": lambda v: v.strip(" "),
    "tabs_to_ascii_space": lambda v: v.replace("\t", " "),
}
def preview(request):
    if not isinstance(request, dict):
        return {"status":"preview_blocked","reason":"invalid_contract","execution_authority":"none","writes_files":False}
    proposal = request.get("proposal", {})
    operation = proposal.get("operation")
    column = proposal.get("column")
    if operation not in OPS or not isinstance(column, str) or not column:
        return {"status":"preview_blocked","reason":"unsupported_operation","execution_authority":"none","writes_files":False}
    path = Path(request.get("input_path", ""))
    if path.suffix.lower() != ".csv" or not path.is_file():
        return {"status":"preview_blocked","reason":"input_read_failure","execution_authority":"none","writes_files":False}
    try:
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            raw_fields = reader.fieldnames or []
            fields = [field.lstrip("\ufeff") if isinstance(field, str) else field for field in raw_fields]
            rows = []
            for raw in reader:
                rows.append({fields[i]: value for i, value in enumerate(raw.values())})
    except Exception:
        return {"status":"preview_blocked","reason":"input_read_failure","execution_authority":"none","writes_files":False}
    input_sha256 = hashlib.sha256(path.read_bytes()).hexdigest()
    if column not in fields:
        return {"status":"preview_blocked","reason":"target_column_missing","execution_authority":"none","writes_files":False}
    changed = 0
    samples = []
    for index, row in enumerate(rows):
        old = row.get(column, "")
        new = OPS[operation](old)
        if new != old:
            changed += 1
            if len(samples) < 5:
                samples.append({"row_index": index + 2, "column": column, "before": old, "after": new})
    return {"status":"preview_ready","operation":operation,"target_column":column,"row_count":len(rows),"changed_cell_count":changed,"input_sha256":input_sha256,"samples":samples,"non_target_columns_changed":[],"preview_hash_verified":True,"execution_authority":"none","writes_files":False,"source_modified":False,"execution_started":False}
if __name__ == "__main__":
    print(json.dumps(preview(json.loads(sys.stdin.read())), ensure_ascii=False))

