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
| Governed web evidence store and allowlisted source adapter | Working; fetch-only, provenance-first, review required |
| Knowledge and capability registry | Working; proposal-to-active promotion requires explicit human review |

## Quick start

The core CLI accepts one JSON envelope on standard input and prints one JSON result. It never executes a command or calls a model by itself. A model-free session preparation example is available in [`examples/session-transport-example.json`](examples/session-transport-example.json), with instructions in [`examples/README.md`](examples/README.md).

```powershell
$env:PYTHONUTF8='1'
Get-Content -Raw -Encoding UTF8 .\example-mediation.json | py -3 .\doaa_algorithmic_cli.py
```

The local file-processing path is separate and documented in `DOAA-LOCAL-README.md`; it requires explicit human approval and writes only to a new approved output path.

## Runtime v1

`doaa_runtime.py` is the local-first coordinator for the current system. It checks the selected library, attempts exact local reuse, checks active knowledge and approved evidence, and returns either a local payload or an explicit adapter/review requirement. It never calls a model, fetches the web, executes a tool, or promotes knowledge by itself. See `CONTRACT-DOAA-RUNTIME-0001.json` and `test_doaa_runtime.py`.

## Structured Command Language v1

`doaa_command_language.py` parses only explicit commands in the form `@library.template key=value`. For example:

```text
@marketing.campaign goal="إطلاق منتج جديد" audience="مطورو برمجيات" channel=web language=ar
```

Registered templates are exact and slot-based: `marketing.campaign`, `sales.pipeline`, `software.task`, and `science.explain`. The parser rejects missing or duplicate slots, unknown slots, malformed quoting, oversized values, and common control symbols. An unknown template produces `governed_capability_request` for contract, threat-model, test, and human review; it is never converted into executable behavior. `DoaaRuntime.prepare_command()` passes accepted commands into the local-first runtime and preserves `execution_authority: none`. See `CONTRACT-DOAA-COMMAND-0001.json`, `ADR-DOAA-COMMAND-LANGUAGE-0001.md`, and `test_doaa_command_language.py`.

## Template-based Reconstruction v1

`doaa_template_reconstruction.py` contains a frozen local registry for the registered templates. `TemplateRegistry.reconstruct()` takes a template identifier and explicit UTF-8 slot data, validates the complete slot set, emits a canonical `doaa.alg.v1` request, and sends it through exact local lookup when used as `DoaaRuntime.prepare_reconstruction()`. It does not infer missing data, create templates, update libraries, call a model, access the network, or execute the reconstructed message. See `CONTRACT-DOAA-RECONSTRUCTION-0001.json` and `test_doaa_template_reconstruction.py`.

## Governed Live Sources v1

`doaa_live_source_adapters.py` provides explicit read-only adapters for Wikimedia summaries and GitHub repository search. Hosts and path prefixes are fixed, HTTPS and safe redirects are required, response sizes and content types are bounded, and returned content is marked untrusted. `build_evidence_record()` creates only a `pending_review` evidence record; approval and any library proposal remain separate human-governed operations. See `CONTRACT-DOAA-LIVE-SOURCES-0001.json`, `ADR-DOAA-LIVE-SOURCES-0001.md`, and `test_doaa_live_source_adapters.py`.

## Governed Learning v1

`doaa_learning_registry.py` records explicit, consented experiences and turns them into candidates without changing the core source or Dody governance. `doaa_learning_loop.py` automates observation and candidate generation only; it never promotes a candidate. `doaa_feedback_gate.py` connects human feedback to candidates while requiring independent evidence for correctness claims. `doaa_confidence.py` keeps usefulness, correctness, safety, and token saving as separate dimensions rather than one misleading truth score. `doaa_reuse_ledger.py` records exact local hits, misses, blocked routes, and observed token savings; it never uses semantic similarity to select an algorithm. `doaa_benchmark.py` computes descriptive comparisons across baseline, local, and model-assisted paths from supplied Arabic cases; its fixtures are schema tests only and cannot support performance claims. `doaa_answer_verifier.py` performs conservative extractive verification against the supplied context; unsupported terms, unseen numbers, and empty answers are sent to explicit retry or human review rather than accepted. `doaa_semantic_checkpoint.py` adds a lossless local checkpoint: the original context remains immutable locally, while a compact reference carries only a checkpoint hash, question, and segment identifiers. On 200 real ArabicaQA cases, the reference averaged 74.0363% smaller than the source and all 200 contexts expanded losslessly; this is storage/reference compression, not proof that a model can answer from an unseen hash. `doaa_goal_gate.py` turns the primary objective into an explicit acceptance rule: token reduction is required, quality cannot regress, and safety must be preserved. A live five-case comparison against `gpt-5-mini` is documented in `MANUS-COMPARISON-2026-08-28.md`; the first independent-request setup failed the goal gate because the Doaa path used more tokens and produced a lower heuristic reference-overlap signal. Warm-session experiments in `MANUS-WARM-SESSION-RESULTS.md` then achieved 72.5344%–73.6346% prompt-token savings and 51.4730%–65.1765% total-token savings, but still failed the quality gate. This is an honest diagnostic result, not a success claim. A candidate can become active only after deterministic validation, benchmark and safety receipts, and explicit human approval. `doaa_learning_evaluator.py` requires token reduction, a minimum quality score, and a passing safety signal; active records can be revoked for rollback. This is continuous improvement, not unrestricted self-modification. See `CONTRACT-DOAA-LEARNING-0001.json`, `ADR-DOAA-LEARNING-0001.md`, and the learning tests.

## Human Feedback v1

`doaa_feedback.py` supports a post-answer question such as «هل كانت الإجابة مفيدة؟» with a usefulness score, a separate correctness signal, optional correction, and explicit consent to learn. Usefulness is treated as a subjective experience signal, while correctness remains an unverified human claim until independent evidence or deterministic validation exists. Positive feedback cannot promote a candidate by itself, and negative feedback can block or trigger review. Feedback has no user identity by default and can be deleted explicitly. See `CONTRACT-DOAA-FEEDBACK-0001.json`, `ADR-DOAA-FEEDBACK-0001.md`, and `test_doaa_feedback.py`.

## Governed algorithm library

Doaa can store explicitly validated `doaa.alg.v1` messages in a local algorithm library and retrieve them by an exact request fingerprint and algorithm identifier. A miss is safe; semantic similarity is not used to guess a reusable algorithm. Registration is explicit, validation is required, persistence is local, and the library never calls a model or executes a stored message. Entries can be browsed under controlled domains: `science`, `industry`, `software`, `business`, `education`, `language`, and `general`, each with fixed subdomains. Classification is for organization and filtering only; it never authorizes reuse. See `CONTRACT-DOAA-ALGORITHM-LIBRARY-0001.json` and `doaa_algorithm_library.py`. The separate [governed web evidence design](WEB-EVIDENCE.md) records sources and review boundaries; it never updates libraries automatically. The [multi-source architecture](DOAA-MULTI-SOURCE-ARCHITECTURE-0001.md) and `doaa_knowledge_registry.py` define how reusable capabilities can be proposed, versioned, reviewed, activated, expired, or revoked without self-modifying the core.

## Governance boundary

Every request and result is bound to `authority: "none"` and `automatic_execution: false. Unknown capabilities are rejected or returned as governed proposals; they are not inferred into executable behavior. New capabilities require a contract, threat-model review, tests, and human approval.

The literal gate is deliberately limited. It can reject new numeric literals, missing required literals, forbidden patterns, and declared shape violations. It does not prove complete semantic entailment. Unverifiable semantic additions must be escalated for human review.

## Testing

Run the project’s script-style tests from the repository root:

```powershell
py -3 -m unittest discover -v
```

Many historical tests execute assertions at import time, so their output reports passed assertions even when unittest says `Ran 0 tests`. The release gate is the combined exit status, printed test receipts, manifest verification, and manual review of the security boundary.

## Project map

The central mediation files are `doaa_algorithmic_protocol.py`, `doaa_algorithmic_mediator.py`, `doaa_request_builder.py`, `doaa_handshake.py`, `doaa_session_protocol.py`, and `doaa_literal_gate.py`. Runtime, command, reconstruction, source, and learning files include `doaa_runtime.py`, `doaa_command_language.py`, `doaa_template_reconstruction.py`, `doaa_live_source_adapters.py`, `doaa_learning_registry.py`, `doaa_learning_loop.py`, `doaa_learning_evaluator.py`, `doaa_feedback.py`, `doaa_feedback_gate.py`, `doaa_confidence.py`, `doaa_reuse_ledger.py`, `doaa_benchmark.py`, `doaa_goal_gate.py`, `doaa_answer_verifier.py`, and `evaluate_warm_run.py`. Knowledge files include `doaa_algorithm_library.py`, `doaa_knowledge_registry.py`, `doaa_web_evidence.py`, and `doaa_web_source_connector.py`. Contracts and ADRs define the governance boundary. Experimental benchmark reports are retained as evidence and clearly marked as non-general guarantees.

## Community tasks

The current contributor tasks are listed in the [GitHub Issues](https://github.com/saifromih-glitch/doaa-prism-engine/issues). Start with [Contributor quickstart examples](https://github.com/saifromih-glitch/doaa-prism-engine/issues/3) if you are new to the codebase, or review [the stateful session transport task](https://github.com/saifromih-glitch/doaa-prism-engine/issues/1) if you are working on model adapters.

## Contributions

Contributions are welcome. Keep changes narrow, add or update a contract when behavior changes, add deterministic tests, preserve fail-closed behavior, and do not add network access, secret access, autonomous execution, self-modification, or model-training claims to the core without a separately reviewed design.

## License

This project is released under the MIT License; see `LICENSE`.
