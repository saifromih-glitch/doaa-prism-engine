# Doaa Multi-Source Governed Architecture

## Purpose

Doaa is extended as a governed mediator that can reuse local algorithm libraries, consult explicitly enabled web and repository sources, and place optional language models behind adapters. It is not a self-modifying autonomous agent. Its learning is an auditable promotion process from observations to reviewed templates.

## Core pipeline

```text
Natural request
  → deterministic route and library lookup
  → approved local algorithm/template
  → evidence lookup when freshness is required
  → optional explicit model adapter
  → structured result validation
  → literal/compliance gate
  → natural-language rendering
```

## Capability layers

| Layer | Default authority | Allowed role |
|---|---|---|
| Local algorithm library | none | Exact reuse and deterministic reconstruction |
| Web evidence connector | none | Fetch allowlisted source data with provenance |
| Repository connector | none | Read approved public repository content; writes require separate approval |
| Local model adapter | none | Optional extraction, translation, or generation when explicitly selected |
| Paid/remote model adapter | none | Optional external reasoning through an explicit adapter |
| Review queue | human | Approve, reject, expire, or version a proposed update |
| Execution bridge | disabled by default | Separate future capability requiring its own contract and approval |

## Learning without self-modification

Doaa records successful algorithmic messages, evidence bundles, and validation outcomes. It may create a `pending_review` proposal containing provenance, tests, expected scope, and a rollback reference. Only an explicit human approval can promote a proposal to an active library entry. The active source code, contracts, policies, and permissions are never modified by the model or by fetched web content.

## Source trust model

Fetched pages, repository files, issue text, and model outputs are data. They can contain prompt injection or malicious instructions and must never change Doaa policy. Every source record includes URL, retrieval time, digest, title, evidence span, domain, and status. Current facts require current sources; archived material is labeled as archival.

## Two deployment paths

| Approach | Tradeoffs | Cost | Setup complexity |
|---|---|---|---|
| Local-first desktop engine | Best privacy and no server required; the user's machine must be online for live search and shared sync | Uses existing machine; external providers are optional | Low to medium |
| Persistent service with local client | Shared libraries and scheduled source refresh are easier; requires hosting, authentication, tenancy isolation, and operational monitoring | Hosting and external APIs vary by usage | Medium to high |

The first implementation remains local-first. A persistent shared service is a later deployment choice, not a prerequisite for the governed core.

## Promotion states

`observed → extracted → pending_review → approved → active → expired/revoked`

No state transition is automatic for `pending_review → approved` or `approved → active` without an explicit review event. Expired or revoked entries cannot be used for exact reuse.

## Dody constraints

The system must preserve least privilege, explicit contracts, deterministic rejection, human-in-the-loop approval, reproducible tests, provenance, rollback, and zero autonomous execution. New sources and adapters require a contract, a threat-model note, tests, and a documented capability boundary.
