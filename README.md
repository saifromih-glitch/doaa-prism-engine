# Doaa — Governed Linguistic-Algorithmic Mediator

Doaa (Prism Engine) is an open-source, governed mediator between a human or intelligent agent and a language model. It maps supported natural-language intents to a compact `doaa.alg.v1` message, lets an external model produce a bound result, validates that result, and renders it back to the user.

> The model proposes or transforms text only. It has no execution authority, no self-update authority, and no permission to access files, secrets, networks, or tools through the core mediation path.

## What works now

| Component | Status |
|---|---|
| `doaa.alg.v1` request and result protocol | Working and tested |
| Conservative intent proposer | Working; exact registered capabilities only |
| Session handshake and compact references | Working locally; session-cache economics remain experimental |
| Result validation and safe rendering | Working and fail-closed |
| Literal-compliance gate | Working; checks explicit machine-testable constraints |
| Arabic UTF-8 support | Supported |
| Ollama bridge | Available as an external/local adapter |
| Direct hosted-model integration | Intentionally external and not required by the core |

## Quick start

The core CLI accepts one JSON envelope on standard input and prints one JSON result. It never executes a command or calls a model by itself. A model-free session preparation example is available in [`examples/session-transport-example.json`](examples/session-transport-example.json), with instructions in [`examples/README.md`](examples/README.md).

```powershell
$env:PYTHONUTF8='1'
Get-Content -Raw -Encoding UTF8 .\example-mediation.json | py -3 .\doaa_algorithmic_cli.py
```

The local file-processing path is separate and documented in `DOAA-LOCAL-README.md`; it requires explicit human approval and writes only to a new approved output path.

## Governance boundary

Every request and result is bound to `authority: "none"` and `automatic_execution: false`. Unknown capabilities are rejected or returned as governed proposals; they are not inferred into executable behavior. New capabilities require a contract, threat-model review, tests, and human approval.

The literal gate is deliberately limited. It can reject new numeric literals, missing required literals, forbidden patterns, and declared shape violations. It does not prove complete semantic entailment. Unverifiable semantic additions must be escalated for human review.

## Testing

Run the project’s script-style tests from the repository root:

```powershell
py -3 -m unittest discover -v
```

Many historical tests execute assertions at import time, so their output reports passed assertions even when unittest says `Ran 0 tests`. The release gate is the combined exit status, printed test receipts, manifest verification, and manual review of the security boundary.

## Project map

The central mediation files are `doaa_algorithmic_protocol.py`, `doaa_algorithmic_mediator.py`, `doaa_request_builder.py`, `doaa_handshake.py`, `doaa_session_protocol.py`, and `doaa_literal_gate.py`. Contracts and ADRs define the governance boundary. Experimental benchmark reports are retained as evidence and clearly marked as non-general guarantees.

## Community tasks

The current contributor tasks are listed in the [GitHub Issues](https://github.com/saifromih-glitch/doaa-prism-engine/issues). Start with [Contributor quickstart examples](https://github.com/saifromih-glitch/doaa-prism-engine/issues/3) if you are new to the codebase, or review [the stateful session transport task](https://github.com/saifromih-glitch/doaa-prism-engine/issues/1) if you are working on model adapters.

## Contributions

Contributions are welcome. Keep changes narrow, add or update a contract when behavior changes, add deterministic tests, preserve fail-closed behavior, and do not add network access, secret access, autonomous execution, self-modification, or model-training claims to the core without a separately reviewed design.

## License

This project is released under the MIT License; see `LICENSE`.
