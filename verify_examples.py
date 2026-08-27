import json
from pathlib import Path
from doaa_session_transport import LocalSessionTransport

e = json.loads(Path('examples/session-transport-example.json').read_text(encoding='utf-8'))
t = LocalSessionTransport(e['session_id'], e['model_language'])
first = t.prepare(e['algorithm_message'])
second = t.prepare(dict(e['algorithm_message'], request_id='demo-002'))
assert first['status'] == 'transport_payload_ready'
assert first['handshake_sent'] is True
assert second['handshake_sent'] is False
assert first['execution_authority'] == 'none'
assert first['automatic_execution'] is False
print('examples_passed')
