# Output Reference Examples

This repository now includes **example output JSON payloads** under:

- `reference/examples/output/`

These files are intended to help an AI coding agent understand the **target payload shape** after generation.

## Included examples

- `bukti-1.example.json`
- `bukti-2.example.json`
- `bukti-3.example.json`
- `bukti-4.example.json`
- `bukti-6.example.json`
- `bukti-7.example.json`

## Important notes

- These are **reference examples**, not final production truth.
- They represent the **best current prototype outputs** we produced while iterating against sample documents.
- Some documents are closer to sample quality than others.

### Closest to sample structure
- Bukti 3
- Bukti 4
- Bukti 6

### Improved but still below best sample quality
- Bukti 1
- Bukti 2
- Bukti 7

### Not included here
- Bukti 5
- Bukti 8

Those were intentionally deprioritized / handled manually in the current prototype phase.

## How to use these examples

Use them as:
- schema-shape references
- output richness references
- renderer input examples
- QA gate baselines

Do **not** assume they are perfect. They are a starting reference for implementation and iteration.

## Recommended usage for AI coding agents

When implementing generation:
1. start from the schema in `docs/carbone-json-generation-final.md`
2. compare generated payloads against these example files
3. validate rendered output against `docs/sample-equivalent-prototype-contract.md`
4. improve prompts/validators until outputs are closer to sample quality
