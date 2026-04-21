# Master Reference

This repository is a **reference package** for an AI-first training document generation architecture.

It is intended to be reused in another application, with no obligation to use the same runtime stack.

## What is included

### 1. Architecture and prompt docs
- `docs/carbone-json-generation-final.md`
- `docs/sample-equivalent-prototype-contract.md`

These documents define:
- minimal interview flow
- SKKNI fetch flow
- `mini_master_data`
- per-bukti generation rules
- exact vs AI-assisted boundaries
- sample-equivalent quality contract
- prompt patterns for generating JSON outputs suitable for document rendering

### 2. Reference implementation (Python)
Located under:

- `reference/python/llma_pipeline/`

This is **not** the mandated production stack.
It exists only to demonstrate the architecture in working code.

The reference implementation contains:
- minimal data adapter
- per-bukti payload building
- per-bukti JSON generation helpers
- per-bukti preview renderers
- JSON → HTML → PDF prototype pipeline

## Important note

The target production system may use:
- React PDF
- Carbone
- Node/TypeScript
- another orchestration runtime

That is fine.

The reusable parts are:
- flow design
- data contracts
- prompt design
- validation rules
- sample-equivalent output expectations

## Suggested usage

1. Start from `docs/sample-equivalent-prototype-contract.md`
2. Read `docs/carbone-json-generation-final.md`
3. Port the data contracts and prompt logic into your production stack
4. Use the Python code only as a behavioral reference, not as a required foundation

## Included example input

- `reference/examples/master_json.sample.json`

This file shows the canonical shape expected by the prototype.

## Secrets

This repository should remain free of production credentials.
Any API keys, DB URLs, or internal document IDs must be provided through environment variables or deployment-specific configuration only.
