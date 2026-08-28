# Manus comparison run — 2026-08-28

## Scope

Five real Arabic cases were sampled from the pinned ArabicaQA `MRC/test` derived benchmark. Each case was sent to `gpt-5-mini` through the Manus-compatible proxy twice: once as a natural baseline prompt and once through the current Doaa protocol prompt. The run made 10 model calls and saved raw outputs in `benchmark-data/arabicaqa/manus-comparison-run.json`.

## Observed results

| Metric | Baseline | Doaa |
|---|---:|---:|
| Prompt tokens | 2,650 | 2,830 |
| Completion tokens | 1,573 | 2,290 |
| Total tokens | 4,223 | 5,120 |
| Mean latency (ms) | 4,600.219 | 6,975.770 |
| Mean reference overlap | 0.540000 | 0.420952 |

Prompt-token change: **-6.7925% saving**, meaning Doaa used 6.7925% more prompt tokens in this run.

Total-token change: **-21.2408% saving**, meaning Doaa used 21.2408% more total tokens in this run.

## Interpretation

This run does not validate the primary goal. The current Doaa request still includes the full QA context, and its protocol/system instructions are longer than the baseline instruction. The model-assisted path also generated longer answers and had lower heuristic reference overlap. The overlap metric is only a heuristic and is not a human truth judgment. Safety was not independently labeled in this run, so no safety conclusion is allowed.

The result is valuable because it identifies the actual bottleneck: Doaa needs a genuinely shorter session handshake and a compact reference mechanism that the model can reliably decode, or it must resolve more requests locally before contacting the model. A protocol wrapper around the same full context is not compression.

## Gate status

The primary goal gate must fail for this run because token usage increased and the heuristic quality signal decreased. No candidate should be promoted from this experiment.
