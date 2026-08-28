# Warm-session compression experiments

## Setup

The same five real Arabic ArabicaQA cases were used in each run with `gpt-5-mini`. The baseline sent each question with the full context in a separate call. The Doaa warm path sent the shared context once and sent five indexed questions in one structured response request. The runs used actual provider `usage` values.

## Results

| Run | Doaa prompt tokens | Doaa total tokens | Prompt saving | Total saving | Baseline overlap | Doaa overlap |
|---|---:|---:|---:|---:|---:|---:|
| v1 | 671 | 1,480 | 73.6346% | 65.1765% | 0.503810 | 0.455238 |
| v2 | 675 | 2,092 | 73.4774% | 51.4730% | 0.469524 | 0.438095 |
| v3 | 699 | 1,674 | 72.5344% | 58.0871% | 0.530476 | 0.334286 |

The baseline varies because the model is nondeterministic. The overlap score is a lexical heuristic, not a human truth judgment. Safety was not independently evaluated in these runs.

## Decision

The warm protocol demonstrates substantial prompt-token compression when one context is shared across several questions. However, the current implementation does not pass the primary goal gate because the heuristic quality signal is lower in all three runs, and the output behavior is not yet stable enough for promotion. No active algorithm or library update is authorized.

The next correction should preserve the shared-context compression while adding a deterministic answer contract: each answer must be a minimal extractive span or a clearly marked `not_found` value, followed by a local validator against context and reference-answer overlap. If validation fails, Doaa must request a model retry or route to human review rather than silently accept the compressed answer.
