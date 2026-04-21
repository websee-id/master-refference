from __future__ import annotations

import importlib
import json
from typing import Any


def build_bukti_2_system_prompt() -> str:
    return (
        "Kamu adalah JSON payload composer untuk template Carbone dokumen Bukti 2 (TNA Mikro). "
        "Output harus JSON valid saja. Jangan output HTML. Jangan output markdown. "
        "Dokumen harus menyerupai TNA Mikro yang formal, rinci, dan cukup panjang. "
        "Wajib ada: organization_profile, program_identity, vision, mission, sdm_analysis, competency_needs_analysis, semester_plan, training_recommendations, conclusion. "
        "Jangan pendek dan jangan hanya 2 paragraf."
    )


def build_bukti_2_prompt(payload: dict[str, Any]) -> str:
    return (
        "Bentuk JSON final untuk Bukti 2: TNA Mikro. "
        "Fokus pada kebutuhan kompetensi mikro dari target peserta, lengkap dengan visi, misi, analisa SDM, standar kinerja, analisis kebutuhan kompetensi, gap kompetensi, rencana pembelajaran semester, dan rekomendasi pelatihan.\n\n"
        f"PAYLOAD:\n{json.dumps(payload, ensure_ascii=False)}"
    )


def generate_bukti_2_json(*, payload: dict[str, Any], settings: Any, client: Any | None = None) -> dict[str, Any]:
    active_client: Any
    generation_allowed = payload.get("generation_allowed")
    if generation_allowed is None:
        generation_allowed = not payload.get("missing_required_inputs", [])
    if not generation_allowed:
        raise ValueError(f"Cannot generate bukti-2; missing inputs: {payload.get('missing_required_inputs', [])}")

    if client is None:
        if not getattr(settings, "gemini_api_key", None):
            raise ValueError("Gemini API key is required for Bukti 2 generation")
        genai = importlib.import_module("google.genai")
        types = importlib.import_module("google.genai.types")
        active_client = genai.Client(api_key=settings.gemini_api_key)
        response = active_client.models.generate_content(
            model=settings.gemini_model,
            contents=build_bukti_2_prompt(payload),
            config=types.GenerateContentConfig(
                temperature=0,
                system_instruction=build_bukti_2_system_prompt(),
                response_mime_type="application/json",
            ),
        )
    else:
        active_client = client
        response = active_client.models.generate_content(
            model=settings.gemini_model,
            contents=build_bukti_2_prompt(payload),
            config=None,
        )

    raw = json.loads((response.text or "").strip())
    return normalize_bukti_2_json(raw, payload)


def normalize_bukti_2_json(raw: dict[str, Any], payload: dict[str, Any]) -> dict[str, Any]:
    context = payload.get("context", {})

    organization_profile = raw.get("organization_profile", {})
    if isinstance(organization_profile, str):
        organization_profile = {
            "organization_name": context.get("organization_name", ""),
            "sector": context.get("sector", ""),
            "business_description": organization_profile,
        }

    program_identity = raw.get("program_identity", {})
    program_identity = {
        "program_name": program_identity.get("program_name") or program_identity.get("nama_program", context.get("program_name", "")),
        "program_goal": program_identity.get("program_goal") or program_identity.get("tujuan_program", context.get("program_goal", "")),
        "target_participants": program_identity.get("target_participants") or program_identity.get("target_peserta", context.get("target_participants", "")),
        "core_problem": program_identity.get("core_problem", context.get("core_problem", "")),
        "competency_focus": program_identity.get("competency_focus") or program_identity.get("fokus_kompetensi", context.get("competency_focus", "")),
    }

    mission = raw.get("mission", [])
    if isinstance(mission, str):
        mission = [part.strip() for part in mission.split(". ") if part.strip()]
    mission = [item.lstrip("1234567890. ") for item in mission]

    sdm_text = raw.get("sdm_analysis", "")
    if isinstance(sdm_text, dict):
        sdm_analysis = sdm_text
    else:
        sdm_analysis = {
            "position_name": _capitalize_first(context.get("target_participants", "Peserta Pelatihan")),
            "function": "Melaksanakan kegiatan utama yang terkait dengan konteks pelatihan.",
            "main_tasks": [
                "Mengidentifikasi masalah utama dalam pekerjaan atau usaha",
                "Menyusun pendekatan penyelesaian yang relevan",
                "Mengevaluasi hasil implementasi strategi",
            ],
            "performance_standards": [
                "Mampu menjalankan tugas dengan pendekatan yang terarah",
                "Mampu mengambil keputusan berdasarkan data dan konteks",
                "Mampu menerapkan hasil pelatihan secara konsisten",
            ],
            "narrative": sdm_text,
        }
    while len(sdm_analysis.get("main_tasks", [])) < 3:
        defaults = [
            "Mengidentifikasi kebutuhan dan masalah utama dalam aktivitas kerja atau usaha",
            "Menyusun dan menjalankan strategi kerja yang relevan dengan tujuan program",
            "Mengevaluasi hasil implementasi dan melakukan perbaikan berkelanjutan",
        ]
        sdm_analysis.setdefault("main_tasks", []).append(defaults[len(sdm_analysis.get("main_tasks", []))])
    while len(sdm_analysis.get("performance_standards", [])) < 3:
        defaults = [
            "Mampu menjalankan tugas dengan pendekatan yang terarah dan terukur",
            "Mampu mengambil keputusan berdasarkan data dan konteks lapangan",
            "Mampu menerapkan hasil pelatihan secara konsisten dalam aktivitas kerja/usaha",
        ]
        sdm_analysis.setdefault("performance_standards", []).append(defaults[len(sdm_analysis.get("performance_standards", []))])

    competency_text = raw.get("competency_needs_analysis", "")
    if isinstance(competency_text, dict):
        competency_needs_analysis = competency_text
    else:
        competency_needs_analysis = {
            "analysis_summary": competency_text,
            "gap_description": competency_text,
            "priority_competencies": [
                "Penerapan strategi kerja yang lebih efektif",
                "Peningkatan kemampuan analisis dan pengambilan keputusan",
                "Penguatan kompetensi inti yang selaras dengan tujuan pelatihan",
            ],
        }

    rec_text = raw.get("training_recommendations", [])
    if isinstance(rec_text, str):
        rec_items = [part.strip() for part in rec_text.split(". ") if part.strip()]
        rec_items = [item.lstrip("1234567890. ") for item in rec_items]
        training_recommendations = [
            {"title": f"Rekomendasi {index + 1}", "description": item}
            for index, item in enumerate(rec_items)
        ]
    else:
        training_recommendations = rec_text

    semester_plan = raw.get("semester_plan")
    if isinstance(semester_plan, list):
        semester_plan = {
            "description": "Rencana pembelajaran semester disusun bertahap untuk memastikan peserta menguasai kompetensi inti.",
            "weekly_plan": [
                {
                    "week": item.get("week", f"Minggu {index + 1}") if isinstance(item, dict) else f"Minggu {index + 1}",
                    "topic": item.get("topic", str(item)) if isinstance(item, dict) else str(item),
                    "learning_outcome": item.get("learning_outcome", "Peserta mencapai target pembelajaran mingguan") if isinstance(item, dict) else "Peserta mencapai target pembelajaran mingguan",
                }
                for index, item in enumerate(semester_plan)
            ],
            "main_references": ["Materi program", "Referensi praktik terbaik"],
        }
    elif not semester_plan and isinstance(raw.get("rencana_pembelajaran_semester"), str):
        semester_plan = {
            "description": raw.get("rencana_pembelajaran_semester", ""),
            "weekly_plan": [
                {"week": "Minggu 1", "topic": "Pengantar materi", "learning_outcome": "Peserta memahami fondasi materi inti"},
                {"week": "Minggu 2", "topic": "Praktik terarah", "learning_outcome": "Peserta mampu menerapkan materi secara langsung"},
            ],
            "main_references": ["Materi internal", "Referensi praktik terbaik"],
        }
    elif isinstance(semester_plan, str):
        semester_plan = {
            "description": semester_plan,
            "weekly_plan": [
                {"week": "Minggu 1", "topic": "Pengantar materi", "learning_outcome": "Peserta memahami fondasi materi inti"},
                {"week": "Minggu 2", "topic": "Praktik terarah", "learning_outcome": "Peserta mampu menerapkan materi secara langsung"},
            ],
            "main_references": ["Materi internal", "Referensi praktik terbaik"],
        }
    elif not semester_plan:
        semester_plan = {
            "description": "Rencana pembelajaran semester disusun untuk memastikan peserta menguasai kompetensi inti secara bertahap dan terukur.",
            "weekly_plan": [
                {"week": "Minggu 1", "topic": "Orientasi kompetensi", "learning_outcome": "Peserta memahami tujuan dan struktur pembelajaran"},
                {"week": "Minggu 2", "topic": "Pendalaman praktik", "learning_outcome": "Peserta dapat mengaplikasikan materi pada konteks kerja/usaha"},
            ],
            "main_references": ["Panduan program", "Referensi teknis yang relevan"],
        }

    return {
        "document_type": "bukti-2",
        "document_title": raw.get("document_title", "TRAINING NEED ANALYSIS"),
        "document_subtitle": raw.get("document_subtitle", "TNA MIKRO"),
        "organization_profile": organization_profile,
        "program_identity": program_identity,
        "vision": raw.get("vision", ""),
        "mission": mission,
        "sdm_analysis": sdm_analysis,
        "competency_needs_analysis": competency_needs_analysis,
        "semester_plan": semester_plan,
        "training_recommendations": training_recommendations,
        "conclusion": raw.get("conclusion", ""),
        "sign_off": {
            "prepared_by": context.get("trainer_name", "Trainer Utama"),
            "city": context.get("organization_city", ""),
            "date": "21 April 2026",
        },
    }


def _capitalize_first(text: str) -> str:
    if not text:
        return text
    return text[:1].upper() + text[1:]
