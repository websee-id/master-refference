from __future__ import annotations

import importlib
import json
from typing import Any


def build_bukti_1_system_prompt() -> str:
    return (
        "Kamu adalah JSON payload composer untuk template Carbone dokumen Bukti 1 (TNA Makro). "
        "Output harus JSON valid saja. Jangan output HTML. Jangan output markdown. "
        "Dokumen harus panjang, formal, dan menyerupai laporan TNA Makro nyata. "
        "Wajib ada section: pendahuluan, profil wilayah, metodologi, temuan utama, analisis kebutuhan, rekomendasi, kesimpulan. "
        "Bagian profil_wilayah harus dipisah menjadi object dengan field regional_profile, business_landscape, dan opportunity_summary. Ketiga field itu wajib berbeda isi, tidak boleh copy-paste. "
        "Gunakan fakta exact dari payload apa adanya. AI boleh membantu menyusun konteks wilayah, lanskap usaha, peluang, analisis kebutuhan, dan rekomendasi. "
        "Jangan pendek dan jangan hanya outline."
    )


def build_bukti_1_prompt(payload: dict[str, Any]) -> str:
    return (
        "Bentuk JSON final untuk Bukti 1: TNA Makro. "
        "Isikan section berikut secara lengkap: pendahuluan, profil wilayah, metodologi, temuan utama, analisis kebutuhan, rekomendasi, kesimpulan. "
        "profil_wilayah harus berupa object dengan tiga subsection yang berbeda: regional_profile, business_landscape, opportunity_summary. "
        "Setiap section harus cukup panjang untuk template dokumen formal.\n\n"
        f"PAYLOAD:\n{json.dumps(payload, ensure_ascii=False)}"
    )


def generate_bukti_1_json(*, payload: dict[str, Any], settings: Any, client: Any | None = None) -> dict[str, Any]:
    active_client: Any
    generation_allowed = payload.get("generation_allowed")
    if generation_allowed is None:
        generation_allowed = not payload.get("missing_required_inputs", [])
    if not generation_allowed:
        raise ValueError(f"Cannot generate bukti-1; missing inputs: {payload.get('missing_required_inputs', [])}")

    if client is None:
        if not getattr(settings, "gemini_api_key", None):
            raise ValueError("Gemini API key is required for Bukti 1 generation")
        genai = importlib.import_module("google.genai")
        types = importlib.import_module("google.genai.types")
        active_client = genai.Client(api_key=settings.gemini_api_key)
        response = active_client.models.generate_content(
            model=settings.gemini_model,
            contents=build_bukti_1_prompt(payload),
            config=types.GenerateContentConfig(
                temperature=0,
                system_instruction=build_bukti_1_system_prompt(),
                response_mime_type="application/json",
            ),
        )
    else:
        active_client = client
        response = active_client.models.generate_content(
            model=settings.gemini_model,
            contents=build_bukti_1_prompt(payload),
            config=None,
        )

    raw = json.loads((response.text or "").strip())
    return normalize_bukti_1_json(raw, payload)


def normalize_bukti_1_json(raw: dict[str, Any], payload: dict[str, Any]) -> dict[str, Any]:
    context = payload.get("context", {})
    raw_region = raw.get("profil_wilayah", {})
    if isinstance(raw_region, str):
        raw_region = {
            "regional_profile": raw_region,
            "business_landscape": raw.get("generated_business_landscape", raw_region),
            "opportunity_summary": raw.get("generated_opportunity_summary", raw_region),
        }
    findings_text = raw.get("temuan_utama", "")
    findings = [part.strip() for part in findings_text.split(".") if part.strip()]
    while len(findings) < 3:
        findings.append("Temuan kebutuhan pelatihan tambahan perlu dikaji lebih lanjut")

    recommendation_text = raw.get("rekomendasi", "")
    recommendations = [part.strip() for part in recommendation_text.split(".") if part.strip()]
    while len(recommendations) < 2:
        recommendations.append("Lakukan tindak lanjut pelatihan agar implementasi berjalan konsisten")

    return {
        "document_type": "bukti-1",
        "document_title": raw.get("document_title", "TRAINING NEED ANALYSIS"),
        "document_subtitle": raw.get("document_subtitle", "TNA MAKRO"),
        "program_title": raw.get("program_title", context.get("program_name", raw.get("program_name", ""))),
        "region_context": {
            "primary_region": context.get("training_location", raw.get("training_location", "")),
            "organization_city": raw.get("organization_city", context.get("organization_city", "")),
            "sector": raw.get("sector", context.get("sector", "")),
            "generated_regional_profile": raw_region.get("regional_profile", raw.get("generated_regional_profile", "")),
            "generated_business_landscape": raw_region.get("business_landscape", raw.get("generated_business_landscape", raw.get("generated_regional_profile", ""))),
            "generated_opportunity_summary": raw_region.get("opportunity_summary", raw.get("generated_opportunity_summary", raw.get("generated_regional_profile", ""))),
        },
        "introduction": {
            "background": raw.get("pendahuluan", raw.get("generated_background", "")),
            "problem_statement": raw.get("problem_statement", context.get("core_problem", raw.get("core_problem", ""))),
            "training_objective": raw.get("generated_objective", context.get("program_goal", raw.get("program_goal", ""))),
        },
        "competency_reference": {
            "unit_code": context.get("unit_code", ""),
            "unit_title": context.get("unit_title", ""),
            "summary": raw.get("competency_summary", context.get("competency_focus", raw.get("competency_focus", ""))),
        },
        "methodology": {
            "approach_summary": raw.get("metodologi", raw.get("generated_methodology", "")),
            "methods_used": raw.get(
                "methods_used",
                [
                    {"name": "Analisis konteks wilayah", "description": "Meninjau kondisi usaha dominan di wilayah sasaran."},
                    {"name": "Analisis kebutuhan kompetensi", "description": "Menghubungkan masalah utama peserta dengan kompetensi yang dibutuhkan."},
                ],
            ),
        },
        "key_findings": [
            {"title": f"Temuan {index + 1}", "description": item}
            for index, item in enumerate(findings[:3])
        ],
        "needs_analysis": {
            "current_condition": raw.get("current_condition", raw.get("pendahuluan", "")),
            "gap_analysis": raw.get("analisis_kebutuhan", raw.get("gap_analysis", "")),
            "priority_needs": raw.get(
                "priority_needs",
                [
                    "Penentuan target audiens yang tepat",
                    "Penyusunan strategi promosi digital yang efisien",
                    "Evaluasi performa kampanye secara berkala",
                ],
            ),
        },
        "recommendations": [
            {"title": f"Rekomendasi {index + 1}", "description": item}
            for index, item in enumerate(recommendations[:2])
        ],
        "conclusion": raw.get("kesimpulan", ""),
        "sign_off": {
            "prepared_by": context.get("trainer_name", ""),
            "city": context.get("organization_city", ""),
            "date": "21 April 2026",
        },
    }
