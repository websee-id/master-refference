from __future__ import annotations

from typing import Any


def adapt_ai_document_master_json(master_json: dict[str, Any]) -> dict[str, Any]:
    brainstorming = master_json.get("brainstorming_master", {})
    training = master_json.get("training", {})
    unit = master_json.get("unit", {})
    competency_map = master_json.get("competency_map", {})
    program_name = brainstorming.get("program_name", "")
    trainer_name = (
        brainstorming.get("trainer_name")
        or master_json.get("people", {}).get("trainer", {}).get("name")
        or master_json.get("document", {}).get("prepared_by", {}).get("name")
        or "Trainer Utama"
    )
    location = brainstorming.get("training_location", "")

    return {
        "organization": {
            "name": brainstorming.get("organization_name", ""),
            "city": brainstorming.get("organization_city", ""),
            "sector": training.get("field") or brainstorming.get("organization_focus", ""),
        },
        "program": {
            "name": program_name,
            "goal": brainstorming.get("program_goal", ""),
            "target_participants": brainstorming.get("target_participants", ""),
            "core_problem": brainstorming.get("industry_problem", ""),
            "competency_focus": unit.get("instructional_goal") or training.get("name", "") or unit.get("name", ""),
            "location": location,
            "duration": _normalize_duration(
                brainstorming.get("training_duration", ""),
                training.get("duration", {}).get("total_jp"),
            ),
            "delivery_method": str(brainstorming.get("delivery_method", "")).lower(),
            "evaluation_methods": _normalize_evaluation_methods(brainstorming.get("evaluation_methods", "")),
            "expected_outcomes": [],
            "field": training.get("field", brainstorming.get("organization_focus", "")),
        },
        "training": {
            "name": training.get("name", program_name),
            "field": training.get("field", brainstorming.get("organization_focus", "")),
            "duration_total_jp": training.get("duration", {}).get("total_jp"),
        },
        "skkni": {
            "selected_unit_codes": [unit.get("code")] if unit.get("code") else [],
            "selected_unit_snapshots": [
                {
                    "unitCode": unit.get("code", ""),
                    "unitTitle": unit.get("name", ""),
                }
            ]
            if unit.get("code")
            else [],
            "selected_unit_details": [
                {
                    "unitCode": unit.get("code", ""),
                    "unitTitle": unit.get("name", ""),
                    "unitDescription": unit.get("description", ""),
                    "map": {
                        "tujuanUtama": competency_map.get("main_goal", ""),
                        "fungsiKunci": competency_map.get("key_function", ""),
                        "fungsiUtama": competency_map.get("main_function", ""),
                        "fungsiDasar": competency_map.get("basic_function", ""),
                    },
                    "elements": [_normalize_element(element) for element in unit.get("elements", [])],
                    "requiredKnowledge": unit.get("required_knowledge", []),
                    "requiredSkills": unit.get("required_skills", []),
                    "workAttitudes": unit.get("work_attitudes", []),
                    "criticalAspects": unit.get("critical_aspects", []),
                    "assessmentContext": unit.get("assessment_context", []),
                    "variableConstraints": unit.get("variable_constraints", {}),
                }
            ]
            if unit.get("code")
            else [],
        },
        "delivery_evidence": {
            "platform": "Google Classroom",
            "class_name": f"{program_name} Batch 1" if program_name else "Kelas Pelatihan Batch 1",
            "teacher_name": trainer_name,
            "assignment_examples": [
                {
                    "title": f"Tugas Utama {training.get('name', program_name) or 'Pelatihan'}",
                    "instructions": f"Susun praktik penerapan materi untuk program {program_name or 'pelatihan'} secara ringkas dan aplikatif.",
                    "points": 100,
                    "due_date": master_json.get("document", {}).get("date_text", ""),
                    "topic": training.get("field", brainstorming.get("organization_focus", "")) or "Pelatihan",
                    "rubric": "Kelengkapan, relevansi, dan ketepatan penerapan materi",
                    "attachments": [],
                }
            ],
        },
        "partnership": {
            "document_number": f"DRAFT/{(program_name or 'PROGRAM')[:12].upper()}",
            "agreement_date": master_json.get("document", {}).get("date_text", ""),
            "agreement_location": location,
            "party_one": {
                "organization_name": brainstorming.get("organization_name", ""),
                "representative_name": master_json.get("document", {}).get("prepared_by", {}).get("name", ""),
                "representative_title": master_json.get("document", {}).get("prepared_by", {}).get("role", ""),
                "address": brainstorming.get("organization_city", ""),
            },
            "party_two": {
                "organization_name": "Mitra Pelatihan Indonesia",
                "representative_name": "Perwakilan Mitra",
                "representative_title": "Direktur",
                "address": location,
            },
            "program_scope": program_name,
            "cost_estimate": _estimate_cost(training.get("duration", {}).get("total_jp"), training.get("field", "")),
            "payment_terms": "50% di muka dan 50% setelah pelatihan selesai",
        },
        "evaluation_summary": {
            "trainer_name": trainer_name,
            "participant_count": 20,
            "feedback_count": 18,
            "quantitative_results": [
                {"aspect": "materi", "scale": "1-4", "scores": [4, 4, 3]},
                {"aspect": "penyampaian", "scale": "1-4", "scores": [4, 3, 4]},
                {"aspect": "aplikasi", "scale": "1-4", "scores": [4, 4, 4]},
            ],
            "qualitative_feedback": [
                "Materi relevan dengan kebutuhan peserta",
                "Sesi praktik membantu pemahaman konsep",
            ],
            "conclusion": f"Pelatihan {program_name or ''} berjalan baik dan peserta menunjukkan respons positif terhadap materi yang diberikan.",
            "recommendations": [
                "Tambahkan studi kasus kontekstual",
                "Lanjutkan dengan sesi pendampingan lanjutan",
            ],
        },
    }


def _normalize_duration(duration_text: str, total_jp: int | None) -> dict[str, Any]:
    if total_jp is not None:
        return {"value": total_jp, "unit": "jp"}
    if duration_text:
        return {"value": duration_text, "unit": "text"}
    return {"value": None, "unit": "hari"}


def _normalize_evaluation_methods(value: Any) -> list[str]:
    if isinstance(value, list):
        return [str(item) for item in value if str(item).strip()]
    if isinstance(value, str) and value.strip():
        return [value.strip()]
    return []


def _normalize_element(element: dict[str, Any]) -> dict[str, Any]:
    return {
        "elementNumber": element.get("element_no") or element.get("element_number") or 0,
        "elementTitle": element.get("element_text") or element.get("element_title") or "",
        "performanceCriteria": [
            {
                "code": kuk.get("kuk_id") or kuk.get("code") or "",
                "description": kuk.get("kuk_text") or kuk.get("description") or "",
            }
            for kuk in element.get("kuk", [])
        ],
    }


def _estimate_cost(total_jp: Any, field: str) -> int:
    try:
        jp = int(total_jp or 10)
    except (TypeError, ValueError):
        jp = 10
    base = 3500000 if str(field).lower() == 'pemasaran' else 3000000
    return base * jp
