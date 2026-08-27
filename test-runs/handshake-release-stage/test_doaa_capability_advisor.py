import json
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent))
import doaa_capability_advisor as a
known=a.advise({'goal':'normalize_ascii_spaces'})
assert known['status']=='known_capability' and known['execution_authority']=='none'
new=a.advise({'goal':'أريد قدرة تحليل صور جديدة'})
assert new['status']=='governed_capability_request' and 'create_code' in new['prohibited_actions']
bad=a.advise({'goal':123})
assert bad['status']=='governed_capability_request'
print(json.dumps({'tests':3,'status':'passed','new_goal_not_built':True,'automatic_execution':False},ensure_ascii=False))
