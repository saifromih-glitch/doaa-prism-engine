# Real benchmark data

The first real benchmark sample is derived from the `MRC/test` split of [ArabicaQA](https://huggingface.co/datasets/abdoelsayed/ArabicaQA). The source file is not modified. The derived `test-cases.json` contains the first 200 answerable Arabic records in source order and preserves the source question identifier.

Source file: `MRC-test.json`

Source SHA-256: `df5c258325afa6d87fca1b9022cec1eff81fa099e0b00241837f92fc55c38fd4`

Derived case count: `200`

The loader and derivation script are `build_arabicaqa_benchmark.py` and `validate_real_benchmark.py`. The derived file is a real-data benchmark input, not a synthetic performance result. No quality, latency, or token-saving claim is valid until the same cases are run through the baseline and Doaa paths and the resulting outputs are independently reviewed.
