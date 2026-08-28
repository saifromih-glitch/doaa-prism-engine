# Semantic Checkpoint + Manus result

## Experiment

Five real Arabic ArabicaQA cases were sent to `gpt-5-mini`. The baseline used five independent natural prompts. The Doaa path registered the context through `WarmCheckpointSession`, sent the source once in a compact checkpoint envelope, and sent indexed question references in the same model request. The expanded checkpoint was then used for local answer verification.

## Observed results

| Metric | Baseline | Doaa checkpoint |
|---|---:|---:|
| Model calls | 5 | 1 |
| Prompt tokens | 2,545 | 1,126 |
| Total tokens | 4,029 | 2,103 |
| Prompt-token saving | — | 55.7564% |
| Total-token saving | — | 47.8034% |
| Mean heuristic reference overlap | 0.393333 | 0.374286 |
| Safety evaluation | not run | not run |

The prompt and total-token reductions are real provider usage values for this run. The overlap metric is lexical and is not a human truth evaluation.

## Verification result

The local extractive verifier accepted 3 of 5 Doaa answers as supported by the expanded source. Two answers were routed to fallback or human review. No automatic retry, library update, or promotion occurred.

## Decision

The checkpoint integration proves meaningful compression while preserving a reversible local copy of the context. It does not yet pass the full goal gate because the heuristic quality signal is slightly lower and two answers failed the conservative support verifier. The implementation must not be promoted as a general solution until answer extraction, retry/fallback behavior, and independent safety evaluation are improved.
