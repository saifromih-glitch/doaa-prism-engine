# Benchmark source findings

## ArabicaQA

URL: https://huggingface.co/datasets/abdoelsayed/ArabicaQA

The dataset card identifies the task as Arabic question answering, shows an MIT license, and lists train, validation, and test splits. The card reports MRC and open-domain variants. Its viewer currently cannot infer the JSON features because the records are nested under a `data` field; a custom loader must account for that structure. This source is a candidate for the real benchmark after checking the repository snapshot, file hashes, and license terms.

## Masader

URL: https://arbml.github.io/masader/

Masader is an Arabic NLP dataset catalogue and discovery index. It should be used to identify additional domain or dialect datasets, not treated as a dataset itself. Each selected dataset requires its own license, provenance, schema, and quality review.

## Decision

Use ArabicaQA as the first benchmark candidate because it is directly oriented to Arabic QA and exposes a public card with a stated MIT license. Do not publish performance claims until a pinned snapshot is downloaded and parsed successfully. Internal fixtures remain schema tests only.
