import json
import tempfile
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent))
import doaa_static_verifier as v
with tempfile.TemporaryDirectory() as t:
    safe=Path(t)/'safe.py'; unsafe=Path(t)/'unsafe.py'
    safe.write_text('def execute(x):\n    return x\n',encoding='utf-8')
    unsafe.write_text('import subprocess\n',encoding='utf-8')
    assert v.verify([safe])["status"]=='static_verification_passed'
    assert v.verify([unsafe])["status"]=='static_verification_blocked'
print(json.dumps({'tests':2,'status':'passed','static_scan_read_only':True,'automatic_execution':False},ensure_ascii=False))
