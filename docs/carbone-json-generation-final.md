# Carbone JSON Generation Final

## Purpose

This document is the final reference for building an **AI-first JSON generation system** for Carbone.

The system goal is:

1. collect only minimal exact interview data,
2. fetch exact SKKNI data from API,
3. compose `mini_master_data`,
4. enable **Generate All Dokumen**,
5. generate **JSON payloads** for `bukti-1` to `bukti-8`,
6. pass those JSON payloads into Carbone templates.

The AI must generate **JSON**, not HTML.

---

## Final Flow

```text
Minimal interview
→ SKKNI selection
→ Fetch /map/{unitCode}
→ Fetch /unit/{unitCode}
→ Compose mini_master_data
→ Preflight check
→ Enable Generate All Dokumen button
→ Build per-bukti payload input
→ Generate per-bukti JSON payload
→ Carbone renders final docs
```

---

## Minimal Interview Data

### Required exact
- `organization_name`
- `organization_city`
- `trainer_name`
- `program_name`
- `program_goal`
- `target_participants`
- `industry_problem`
- `training_location`
- `training_duration`
- `selected_unit_code`

### Recommended but non-blocking
- `delivery_method`

### Conditional only if needed
- `partner_name` *(for more realistic Bukti 7)*

---

## Mini Master Data Shape

```json
{
  "brainstorming_master": {
    "organization_name": "PT Obayito",
    "organization_city": "Bekasi",
    "trainer_name": "Budi Santoso",
    "program_name": "Pelatihan Digital Marketing untuk UMK",
    "program_goal": "Meningkatkan penjualan UMKM melalui strategi digital",
    "target_participants": "owner UMKM",
    "industry_problem": "iklan boros tapi hasil minim",
    "training_location": "Jakarta",
    "training_duration": "2 hari",
    "delivery_method": "online"
  },
  "skkni_selection": {
    "selected_unit_code": "N.79JPW00.139.1",
    "selected_unit_title": "Mengembangkan Strategi Peningkatan Penjualan Media Digital"
  },
  "skkni_map": {},
  "skkni_unit_detail": {},
  "partnership_minimal": {
    "partner_name": ""
  },
  "generation_mode": "ai_assisted",
  "generation_ready_core": false,
  "generation_gaps_optional": []
}
```

---

## Preflight Rules

### Core ready blockers
- `organization_name`
- `organization_city`
- `trainer_name`
- `program_name`
- `program_goal`
- `target_participants`
- `industry_problem`
- `training_location`
- `training_duration`
- `selected_unit_code`
- `/map/{unitCode}` fetch success
- `/unit/{unitCode}` fetch success

### Optional gaps (do not block Generate All)
- missing `delivery_method`
- missing `partner_name`
- no detailed delivery evidence
- no evaluation summary

### Example state

```json
{
  "generation_ready_core": true,
  "generation_gaps_optional": [
    "partner_name"
  ]
}
```

---

## Per-Bukti Truth Model

| Bukti | Mode | Main source |
|---|---|---|
| 1 | AI-assisted | brainstorming + selected unit context |
| 2 | AI-assisted | brainstorming + selected unit context |
| 3 | exact-heavy | `/map/{unitCode}` |
| 4 | exact-heavy | `/unit/{unitCode}` |
| 5 | AI-assisted | brainstorming + trainer + optional delivery hints |
| 6 | AI-assisted | brainstorming + strong marketing schema |
| 7 | hybrid-template | exact identities + AI legal wording |
| 8 | AI-assisted | trainer + participant context + AI evaluation structure |

---

## Global System Prompt for JSON Generation

```text
Kamu adalah JSON payload composer untuk template dokumen Carbone.

Tugasmu adalah membentuk JSON final untuk dokumen yang diminta.

Aturan:
- Output harus JSON valid saja.
- Jangan output HTML.
- Jangan output markdown.
- Jangan output penjelasan.
- Pertahankan semua field exact dari payload apa adanya.
- Isi field generated hanya pada area yang memang boleh AI-assisted.
- Jangan mengarang exact facts yang tidak ada di payload.
- Jika field exact kosong dan memang wajib, biarkan kosong/null sesuai schema; jangan menebak.
- Isi section generated secara kaya, panjang, dan siap dipakai template dokumen formal.
- Jangan membuat output minim/outline pendek. Setiap section wajib harus terisi secara memadai.
```

---

## Bukti 1

### Final JSON Schema

```json
{
  "document_type": "bukti-1",
  "document_title": "TRAINING NEED ANALYSIS",
  "document_subtitle": "TNA MAKRO",
  "program_title": "",
  "region_context": {
    "primary_region": "",
    "organization_city": "",
    "sector": "",
    "generated_regional_profile": "",
    "generated_business_landscape": "",
    "generated_opportunity_summary": ""
  },
  "introduction": {
    "background": "",
    "problem_statement": "",
    "training_objective": ""
  },
  "competency_reference": {
    "unit_code": "",
    "unit_title": "",
    "summary": ""
  },
  "methodology": {
    "approach_summary": "",
    "methods_used": [
      {
        "name": "",
        "description": ""
      }
    ]
  },
  "key_findings": [
    {
      "title": "",
      "description": ""
    }
  ],
  "needs_analysis": {
    "current_condition": "",
    "gap_analysis": "",
    "priority_needs": [
      ""
    ]
  },
  "recommendations": [
    {
      "title": "",
      "description": ""
    }
  ],
  "conclusion": "",
  "sign_off": {
    "prepared_by": "",
    "city": "",
    "date": ""
  }
}
```

### Prompt

```text
Bentuk JSON final untuk Bukti 1: TNA Makro.

Dokumen harus menyerupai laporan TNA makro yang panjang dan formal.

Wajib ada:
- pendahuluan
- profil wilayah
- metodologi
- temuan utama
- analisis kebutuhan
- rekomendasi
- kesimpulan

Gunakan exact facts dari payload apa adanya.
AI boleh menyusun konteks wilayah, profil usaha dominan, peluang bisnis, analisis kebutuhan, dan rekomendasi berdasarkan wilayah, sektor, tujuan pelatihan, target peserta, masalah utama, dan unit kompetensi yang dipilih.

Jangan pendek.
Jangan buat cuma outline.
Isi setiap section dengan narasi yang cukup panjang untuk dipakai template dokumen.
Output hanya JSON valid.
```

### Validator
- `key_findings.length >= 3`
- `recommendations.length >= 2`
- `introduction.background` not empty
- `needs_analysis.gap_analysis` not empty
- `conclusion` not empty

---

## Bukti 2

### Final JSON Schema

```json
{
  "document_type": "bukti-2",
  "document_title": "TRAINING NEED ANALYSIS",
  "document_subtitle": "TNA MIKRO",
  "organization_profile": {
    "organization_name": "",
    "sector": "",
    "business_description": ""
  },
  "program_identity": {
    "program_name": "",
    "program_goal": "",
    "target_participants": "",
    "core_problem": "",
    "competency_focus": ""
  },
  "vision": "",
  "mission": [
    ""
  ],
  "sdm_analysis": {
    "position_name": "",
    "function": "",
    "main_tasks": [
      ""
    ],
    "performance_standards": [
      ""
    ]
  },
  "competency_needs_analysis": {
    "analysis_summary": "",
    "gap_description": "",
    "priority_competencies": [
      ""
    ]
  },
  "training_recommendations": [
    {
      "title": "",
      "description": ""
    }
  ],
  "conclusion": "",
  "sign_off": {
    "prepared_by": "",
    "city": "",
    "date": ""
  }
}
```

### Prompt

```text
Bentuk JSON final untuk Bukti 2: TNA Mikro.

Dokumen harus menyerupai TNA Mikro yang formal, rinci, dan cukup panjang.

Wajib ada:
- organization_profile
- program_identity
- vision
- mission
- sdm_analysis
- competency_needs_analysis
- training_recommendations
- conclusion

Jangan pendek.
Jangan buat hanya 2 paragraf.
AI boleh menyusun visi, misi, analisa SDM, gap kompetensi, dan rekomendasi secara kaya berdasarkan konteks program dan unit kompetensi.
Output hanya JSON valid.
```

### Validator
- `vision` not empty
- `mission.length >= 2`
- `sdm_analysis.main_tasks.length >= 3`
- `sdm_analysis.performance_standards.length >= 3`
- `training_recommendations.length >= 2`

---

## Bukti 3

### Final JSON Schema

```json
{
  "document_type": "bukti-3",
  "document_title": "PEMETAAN KOMPETENSI",
  "unit_code": "",
  "rows": [
    {
      "tujuan_utama": "",
      "fungsi_kunci": "",
      "fungsi_utama": "",
      "fungsi_dasar": ""
    }
  ],
  "document_city": "",
  "document_date": "",
  "prepared_by": ""
}
```

### Prompt

```text
Bentuk JSON final untuk Bukti 3: Pemetaan Kompetensi.

Gunakan data map exact dari payload.
Jangan mengarang isi row.
Kamu hanya menyusun struktur tabel final dan metadata dokumen.
Output hanya JSON valid.
```

### Validator
- `rows.length >= 1`
- every row has `tujuan_utama`, `fungsi_kunci`, `fungsi_dasar`

---

## Bukti 4

### Final JSON Schema

```json
{
  "document_type": "bukti-4",
  "unit_code": "",
  "unit_title": "",
  "unit_description": "",
  "elements": [
    {
      "element_number": 0,
      "element_title": "",
      "performance_criteria": [
        {
          "code": "",
          "description": ""
        }
      ]
    }
  ],
  "required_knowledge": [
    ""
  ],
  "required_skills": [
    ""
  ],
  "work_attitudes": [
    ""
  ],
  "critical_aspects": [
    ""
  ],
  "assessment_context": [],
  "variable_constraints": {}
}
```

### Prompt

```text
Bentuk JSON final untuk Bukti 4: Unit Kompetensi.

Gunakan data exact dari payload unit detail.
Jangan mengarang KUK, elemen, pengetahuan, keterampilan, sikap kerja, aspek kritis, atau batasan variabel.
Output hanya JSON valid.
```

### Validator
- `unit_code` not empty
- `unit_title` not empty
- `elements.length >= 1`
- each element has at least 1 performance criteria

---

## Bukti 5

### Final JSON Schema

```json
{
  "document_type": "bukti-5",
  "document_title": "BUKTI PELAKSANAAN KELAS",
  "program_identity": {
    "program_name": "",
    "trainer_name": "",
    "target_participants": "",
    "platform": "",
    "class_name": ""
  },
  "stage_1_create_class": {
    "title": "Tahap 1 – Proses Pembuatan Kelas",
    "description": "",
    "key_points": [
      ""
    ]
  },
  "stage_2_homepage": {
    "title": "Tahap 2 – Tampilan Beranda Kelas",
    "description": "",
    "key_points": [
      ""
    ]
  },
  "stage_3_student_list": {
    "title": "Tahap 3 – Daftar Siswa/Peserta",
    "description": "",
    "student_summary": [
      ""
    ]
  },
  "stage_4_assignment": {
    "title": "Tahap 4 – Pemberian Tugas",
    "assignment_title": "",
    "instructions": "",
    "points": 0,
    "due_date": "",
    "topic": "",
    "rubric": "",
    "attachments": [
      ""
    ],
    "description": ""
  },
  "closing_summary": ""
}
```

### Prompt

```text
Bentuk JSON final untuk Bukti 5: Bukti Pelaksanaan Kelas.

Dokumen ini AI-assisted dan harus terasa seperti bukti proses kelas yang meyakinkan.

Wajib ada 4 tahap:
- Tahap 1 pembuatan kelas
- Tahap 2 tampilan beranda
- Tahap 3 daftar siswa/peserta
- Tahap 4 pemberian tugas

Assignment section harus rinci.
Output hanya JSON valid.
```

### Validator
- all four stages exist
- `stage_4_assignment.assignment_title` not empty
- `stage_4_assignment.instructions` not empty
- `closing_summary` not empty

---

## Bukti 6

### Final JSON Schema

```json
{
  "document_type": "bukti-6",
  "document_title": "MARKETING PLAN",
  "program_identity": {
    "program_name": "",
    "training_name": "",
    "organization_name": "",
    "organization_city": "",
    "sector": "",
    "target_participants": "",
    "delivery_method": "",
    "duration": ""
  },
  "executive_summary": "",
  "marketing_objectives": [
    {
      "objective": "",
      "target_metric": "",
      "timeframe": ""
    }
  ],
  "market_analysis": {
    "current_market_condition": "",
    "target_market_overview": "",
    "problem_context": "",
    "opportunity_analysis": ""
  },
  "market_segments": [
    {
      "segment_name": "",
      "description": "",
      "needs": ""
    }
  ],
  "competitor_analysis": [
    {
      "competitor_name": "",
      "strengths": "",
      "weaknesses": "",
      "positioning_gap": ""
    }
  ],
  "value_proposition": {
    "main_value": "",
    "key_differentiators": [
      ""
    ]
  },
  "marketing_strategy": {
    "product_strategy": "",
    "pricing_strategy": "",
    "promotion_strategy": "",
    "distribution_strategy": "",
    "communication_strategy": ""
  },
  "budget_breakdown": [
    {
      "item": "",
      "amount_idr": 0,
      "description": ""
    }
  ],
  "timeline": [
    {
      "phase": "",
      "activity": "",
      "period": ""
    }
  ],
  "kpi": [
    {
      "name": "",
      "target": "",
      "measurement": ""
    }
  ],
  "conclusion": "",
  "sign_off": {
    "prepared_by": "",
    "city": "",
    "date": ""
  }
}
```

### Prompt

```text
Bentuk JSON final untuk Bukti 6: Marketing Plan.

Dokumen harus berupa marketing plan yang panjang, strategis, dan realistis untuk konteks pelatihan di Indonesia.

Wajib ada:
- executive summary
- marketing objectives
- market analysis
- market segments
- competitor analysis
- value proposition
- marketing strategy
- budget breakdown
- timeline
- KPI
- conclusion

Jangan menghasilkan evaluation report.
Jangan membuat outline pendek.
Output hanya JSON valid.
```

### Validator
- `executive_summary` not empty
- `marketing_objectives.length >= 3`
- `market_segments.length >= 2`
- `competitor_analysis.length >= 2`
- `budget_breakdown.length >= 3`
- `timeline.length >= 3`
- `kpi.length >= 3`
- reject if field like `evaluation_report` appears

---

## Bukti 7

### Final JSON Schema

```json
{
  "document_type": "bukti-7",
  "document_title": "PERJANJIAN KERJASAMA",
  "document_subtitle": "",
  "document_number": "",
  "agreement_date": "",
  "agreement_location": "",
  "party_one": {
    "organization_name": "",
    "representative_name": "",
    "representative_title": "",
    "address": ""
  },
  "party_two": {
    "organization_name": "",
    "representative_name": "",
    "representative_title": "",
    "address": ""
  },
  "premise_points": [
    ""
  ],
  "pasal_1_scope": {
    "title": "RUANG LINGKUP PROGRAM",
    "content": ""
  },
  "pasal_2_execution": {
    "title": "PELAKSANAAN PELATIHAN",
    "content": ""
  },
  "pasal_3_duration": {
    "title": "JANGKA WAKTU PERJANJIAN",
    "content": ""
  },
  "pasal_4_cost": {
    "title": "BIAYA PELATIHAN",
    "content": "",
    "cost_estimate": null
  },
  "pasal_5_payment": {
    "title": "CARA PEMBAYARAN",
    "content": "",
    "payment_terms": ""
  },
  "pasal_6_obligations": {
    "title": "KEWAJIBAN PARA PIHAK",
    "content": ""
  },
  "closing_paragraph": ""
}
```

### Prompt

```text
Bentuk JSON final untuk Bukti 7: draft PKS / MoU.

Dokumen ini template-driven legal draft, bukan final legal authoring engine.

Wajib ada:
- document_title
- agreement_date
- agreement_location
- party_one
- party_two
- premise_points
- pasal 1 sampai pasal 6
- closing_paragraph

Pertahankan exact identity fields.
AI boleh membuat legal wording, pasal, boilerplate formal, dan biaya yang masuk akal jika mode memperbolehkan.
Output hanya JSON valid.
```

### Validator
- `party_one.organization_name` not empty
- `party_two.organization_name` not empty
- `premise_points.length >= 3`
- pasal 1–6 not empty
- `closing_paragraph` not empty

---

## Bukti 8

### Final JSON Schema

```json
{
  "document_type": "bukti-8",
  "document_title": "EVALUASI PELAKSANAAN PELATIHAN",
  "program_identity": {
    "program_name": "",
    "trainer_name": "",
    "participant_count": 0,
    "feedback_count": 0
  },
  "question_results": [
    {
      "question": "",
      "aspect": "",
      "scale": "",
      "score_rows": [
        {
          "label": "",
          "count": 0
        }
      ],
      "summary": ""
    }
  ],
  "qualitative_feedback": [
    ""
  ],
  "conclusion": "",
  "recommendations": [
    ""
  ]
}
```

### Prompt

```text
Bentuk JSON final untuk Bukti 8: Evaluasi Pelaksanaan Pelatihan.

Dokumen harus terasa seperti laporan evaluasi pelatihan yang utuh.

Wajib ada:
- program_identity
- question_results
- qualitative_feedback
- conclusion
- recommendations

question_results harus berisi beberapa pertanyaan evaluasi, masing-masing dengan hasil tabular.
Output hanya JSON valid.
```

### Validator
- `question_results.length >= 3`
- every `score_rows.length >= 2`
- `qualitative_feedback.length >= 1`
- `recommendations.length >= 2`
- `conclusion` not empty

---

## Integration Order

1. apply richer schema for `bukti-1`
2. apply richer schema for `bukti-6`
3. apply richer schema for `bukti-2`
4. apply richer schema for `bukti-7`
5. apply richer schema for `bukti-8`
6. apply richer schema for `bukti-5`
7. rerun generation
8. compare with OCR samples again

---

## What is complete now

You now have:
- minimal interview architecture
- mini master data concept
- generate-all flow
- per-bukti exact vs AI-assisted rules
- richer schemas for 1, 2, 5, 6, 7, 8
- exact-heavy handling for 3 and 4
- final prompt drafts per bukti
- validator rules per bukti

This is enough to move into the next phase: updating the actual generator and rerunning output quality tests.
