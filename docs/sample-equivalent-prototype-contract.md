# Sample-Equivalent Prototype Contract

## Purpose

This document defines the **prototype target** for the AI document generation system.

The prototype is **successful** only when the generated content is **close in structure, density, and tone** to the parsed sample documents.

This prototype is **not** primarily about final PDF rendering. Final PDF rendering can be handled later by React PDF or another renderer.

The prototype must prove:

1. minimal interview data is sufficient,
2. exact API data is pulled where needed,
3. prompts and schemas can produce sample-like content,
4. each document type has clear exact-vs-generated boundaries,
5. a simple preview renderer can show whether the content is good enough.

---

## What “Setara Sample” Means

A generated document is considered **sample-equivalent** when it satisfies all of the following:

### 1. Structural match
- The output contains the same major sections as the sample.
- The output order feels similar to the sample.
- Tables/lists appear where the sample also uses tables/lists.

### 2. Content density match
- The output is not a short summary.
- The output is not a field dump.
- Each major section contains enough content to feel like a real document section.

### 3. Tone match
- The tone is formal, administrative, and document-like.
- It should not feel like chat output, bullet notes, or AI outline mode.

### 4. Exact fact safety
- Exact facts from user or API remain unchanged.
- The generator does not invent codes, names, legal identities, or competency details.

### 5. Prototype renderer sufficiency
- Even with a plain renderer, the content should already look document-shaped.
- Rendering quality is secondary; content quality is primary.

---

## Prototype Boundaries

### In scope
- minimal data collection
- SKKNI exact fetch
- per-bukti payloads
- per-bukti prompt design
- per-bukti schema design
- per-bukti validation
- simple preview rendering

### Out of scope for now
- pixel-perfect layout
- production React PDF design
- full visual styling
- final legal sign-off readiness
- final production UX polish

---

## Final Generation Flow for Prototype

```text
Minimal interview
→ SKKNI selection
→ Fetch /map/{unitCode}
→ Fetch /unit/{unitCode}
→ Build mini_master_data
→ Build per-bukti payload
→ Generate per-bukti content JSON
→ Validate richness + structure + drift
→ Render simple preview
→ Compare to sample
```

---

## Exact vs AI-Generated Contract

### Exact-heavy
- **Bukti 3** → mostly exact from `/map/{unitCode}`
- **Bukti 4** → mostly exact from `/unit/{unitCode}`

### Hybrid
- **Bukti 7** → exact party facts + AI legal wording

### AI-assisted
- **Bukti 1**
- **Bukti 2**
- **Bukti 5**
- **Bukti 6**
- **Bukti 8**

AI-assisted does **not** mean free hallucination.
It means:
- exact facts stay exact,
- AI expands only the allowed narrative fields.

---

## Definition of Done Per Bukti

### Bukti 1 — TNA Makro
Must contain:
- Pendahuluan
- Profil Wilayah
- Referensi Kompetensi
- Metodologi
- Temuan Utama
- Analisis Kebutuhan
- Rekomendasi
- Kesimpulan

Must not:
- collapse into 3 short paragraphs
- duplicate the same paragraph across region/profile/opportunity sections

Prototype acceptance:
- at least 4 pages in preview/PDF-like render is a good sign
- findings and recommendations must be distinct, not repeated prose

### Bukti 2 — TNA Mikro
Must contain:
- Company / organization profile
- Visi
- Misi
- Analisa SDM
- Tugas Pokok
- Standar Kinerja
- Analisis Kebutuhan Kompetensi
- Rekomendasi
- Kesimpulan

Must not:
- reduce to one background paragraph + one recommendation
- skip SDM/task/performance sections

Prototype acceptance:
- at least 2–3 pages in preview/PDF-like render
- mission, tasks, standards, and gap analysis all present

### Bukti 3 — Pemetaan Kompetensi
Must contain:
- Title
- 4-column competency mapping table
- place/date
- prepared_by

Must not:
- invent rows beyond API data

Prototype acceptance:
- exact mapping values present
- document shape visibly matches sample table layout

### Bukti 4 — Unit Kompetensi
Must contain:
- Kode Unit
- Judul Unit
- Deskripsi Unit
- Tabel Elemen + KUK
- Batasan Variabel
- Panduan Penilaian

Must not:
- invent unit details

Prototype acceptance:
- exact-heavy output with multi-page detail

### Bukti 5 — Bukti Pelaksanaan Kelas
Must contain:
- 4 stages
- assignment section with detailed fields
- closing summary

Must not:
- reduce to one paragraph summary

Prototype acceptance:
- reads like a class execution record or simulation, not a memo

### Bukti 6 — Marketing Plan
Must contain:
- Executive Summary
- Marketing Objectives
- Market Analysis
- Market Segments
- Competitor Analysis
- Value Proposition
- Marketing Strategy
- Budget Breakdown
- Timeline
- KPI
- Conclusion

Must not:
- drift into evaluation report language
- omit business sections

Prototype acceptance:
- at least 4–5 pages in preview/PDF-like render is a good sign
- reads like a marketing/business document, not training evaluation

### Bukti 7 — PKS / MoU Draft
Must contain:
- party identities
- premise
- pasal 1–6
- closing paragraph

Must not:
- look like a generic letter
- skip clause structure

Prototype acceptance:
- legal-draft feel, formal tone, multi-section content

### Bukti 8 — Evaluasi Pelatihan
Must contain:
- trainer/program identity
- several evaluation question blocks
- qualitative feedback
- conclusion
- recommendations

Must not:
- become one generic summary paragraph

Prototype acceptance:
- clear evaluation structure with tabular/question-like detail

---

## Validation Layers Required

Every document must pass all of these:

### 1. Schema validation
Does the JSON shape match the target schema?

### 2. Richness validation
Are required sections populated deeply enough?

### 3. Drift validation
Did the document drift into another document family?

Examples:
- Bukti 6 must reject evaluation-style output
- Bukti 3 must reject prose-heavy invented rows
- Bukti 4 must reject missing exact KUKs

### 4. Preview validation
Does the simple renderer already look like a document, not a key-value dump?

---

## Prototype Execution Order

Do **not** try to perfect all 8 at once.

Recommended order:

1. Bukti 1
2. Bukti 6
3. Bukti 2
4. Bukti 7
5. Bukti 8
6. Bukti 5
7. Bukti 3 (mostly exact renderer refinement only)
8. Bukti 4 (mostly exact renderer refinement only)

Rationale:
- 1, 2, 6, 7, 8 are the highest risk for under-detailed AI output
- 3 and 4 are structurally safer because they are API-heavy

---

## Prompting Strategy

### Use per-bukti prompts
Never use one generic generation prompt for all 8 documents.

### Use per-bukti schemas
Never use one generic “generated narrative” schema for all 8.

### Use a repair loop
If output fails validation:
1. keep the same payload
2. feed back the exact failed rules
3. regenerate only that document

---

## Review Protocol

For each document prototype, compare against the sample using these questions:

1. Does the output belong to the correct document family?
2. Does it have the same major sections as the sample?
3. Is it as dense as the sample, or much shorter?
4. Does it feel like a real document, or still like AI-generated notes?
5. Are any exact facts wrong, missing, or invented?

Only move to the next document when the answer is:
- structurally yes
- density close enough
- no major fact drift

---

## Practical Conclusion

For this prototype, success is **not** “the pipeline runs”.

Success is:

> the generated content is close enough to the sample that using better final rendering (for example React PDF or Carbone templates) would plausibly produce a document that feels production-ready.

That is the standard for all further work.
