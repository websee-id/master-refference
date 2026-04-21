from __future__ import annotations

import importlib
import json
import argparse
from pathlib import Path
from typing import Any
from urllib.request import Request, urlopen


def load_master_json(file_path: Path) -> dict[str, Any]:
    return json.loads(file_path.read_text(encoding="utf-8"))


def fetch_json(url: str) -> dict[str, Any]:
    request = Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0",
            "Accept": "application/json,text/html;q=0.9,*/*;q=0.8",
        },
    )
    with urlopen(request) as response:
        return json.loads(response.read().decode("utf-8"))


def build_document_payload(
    document_type: str,
    master_json: dict[str, Any],
    *,
    fetch_json: Any = fetch_json,
) -> dict[str, Any]:
    builder = {
        "bukti-1": _build_bukti_1_payload,
        "bukti-2": _build_bukti_2_payload,
        "bukti-3": _build_bukti_3_payload,
        "bukti-4": _build_bukti_4_payload,
        "bukti-5": _build_bukti_5_payload,
        "bukti-6": _build_bukti_6_payload,
        "bukti-7": _build_bukti_7_payload,
        "bukti-8": _build_bukti_8_payload,
    }[document_type]
    return builder(master_json, fetch_json=fetch_json)


def build_system_prompt(document_type: str) -> str:
    return (
        f"Anda adalah generator dokumen profesional untuk {document_type}. "
        "Hasil akhir harus berupa HTML lengkap dan valid, dimulai dengan <html> dan diakhiri dengan </html>. "
        "Ikuti struktur dokumen yang formal, panjang, dan menyerupai dokumen contoh. "
        "Jangan mengarang data bisnis, API, bukti, nilai evaluasi, identitas pihak, atau isi kompetensi yang tidak ada di payload. "
        "Jika payload kurang, berhenti dan nyatakan kekurangan input dalam HTML secara eksplisit tanpa menambahkan fakta palsu."
    )


def build_user_prompt(document_type: str, payload: dict[str, Any]) -> str:
    return (
        f"Buat dokumen {document_type} dalam HTML lengkap. "
        "Gunakan hanya data pada payload berikut. Pertahankan judul, tabel, daftar, dan blok penutup jika memang relevan dengan tipe dokumen.\n\n"
        f"PAYLOAD:\n{json.dumps(payload, ensure_ascii=False)}"
    )


def generate_html_document(
    *,
    document_type: str,
    payload: dict[str, Any],
    settings: Any,
    client: Any | None = None,
) -> str:
    active_client: Any
    generation_allowed = payload.get("generation_allowed")
    if generation_allowed is None:
        generation_allowed = not payload.get("missing_required_inputs", [])
    if not generation_allowed:
        raise ValueError(f"Cannot generate {document_type}; missing inputs: {payload.get('missing_required_inputs', [])}")
    if client is None:
        if not getattr(settings, "gemini_api_key", None):
            raise ValueError("Gemini API key is required for document generation")
        genai = importlib.import_module("google.genai")
        types = importlib.import_module("google.genai.types")
        active_client = genai.Client(api_key=settings.gemini_api_key)
        response = active_client.models.generate_content(
            model=settings.gemini_model,
            contents=build_user_prompt(document_type, payload),
            config=types.GenerateContentConfig(
                temperature=0,
                system_instruction=build_system_prompt(document_type),
            ),
        )
    else:
        active_client = client
        response = active_client.models.generate_content(
            model=settings.gemini_model,
            contents=build_user_prompt(document_type, payload),
            config=None,
        )

    html = (response.text or "").strip()
    if not html.lower().startswith("<html"):
        html = f"<html><body>{html}</body></html>"
    return html


def generate_all_documents(
    *,
    master_json: dict[str, Any],
    settings: Any,
    output_dir: Path,
    document_types: list[str] | None = None,
    fetch_json_func: Any = fetch_json,
) -> list[Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    for document_type in document_types or [f"bukti-{number}" for number in range(1, 9)]:
        payload = build_document_payload(document_type, master_json, fetch_json=fetch_json_func)
        html = generate_html_document(document_type=document_type, payload=payload, settings=settings)
        out_path = output_dir / f"{document_type}.html"
        out_path.write_text(html, encoding="utf-8")
        written.append(out_path)
    return written


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate HTML bukti documents from master JSON")
    parser.add_argument("--master-json", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, default=Path("outputs"))
    parser.add_argument("--document-type", type=str)
    parser.add_argument("--compile-only", action="store_true")
    args = parser.parse_args()

    from llma_pipeline.config import load_settings

    settings = load_settings()
    master_json = load_master_json(args.master_json)
    document_types = [args.document_type] if args.document_type else [f"bukti-{number}" for number in range(1, 9)]

    if args.compile_only:
        compiled = {
            document_type: build_document_payload(document_type, master_json)
            for document_type in document_types
        }
        print(json.dumps(compiled, ensure_ascii=False, indent=2))
        return

    written = generate_all_documents(
        master_json=master_json,
        settings=settings,
        output_dir=args.output_dir,
        document_types=document_types,
    )
    for path in written:
        print(path)


def _build_bukti_1_payload(master_json: dict[str, Any], *, fetch_json: Any) -> dict[str, Any]:
    snapshots = master_json.get("skkni", {}).get("selected_unit_snapshots", [])
    selected_unit = snapshots[0] if snapshots else {}
    context = {
        "organization_name": master_json["organization"]["name"],
        "organization_city": master_json["organization"].get("city", ""),
        "sector": master_json["organization"].get("sector", ""),
        "program_name": master_json["program"]["name"],
        "program_goal": master_json["program"]["goal"],
        "target_participants": master_json["program"]["target_participants"],
        "core_problem": master_json["program"]["core_problem"],
        "competency_focus": master_json["program"]["competency_focus"],
        "training_location": master_json["program"]["location"],
        "training_duration": _format_duration(master_json["program"].get("duration", {})),
        "delivery_method": master_json["program"].get("delivery_method", ""),
        "trainer_name": master_json.get("delivery_evidence", {}).get("teacher_name", ""),
        "unit_code": selected_unit.get("unitCode", ""),
        "unit_title": selected_unit.get("unitTitle", ""),
    }
    return _make_payload("bukti-1", context, [], ["organization_name", "program_name", "program_goal", "target_participants", "core_problem"])


def _build_bukti_2_payload(master_json: dict[str, Any], *, fetch_json: Any) -> dict[str, Any]:
    context = {
        "organization_name": master_json["organization"]["name"],
        "sector": master_json["organization"].get("sector", ""),
        "program_name": master_json["program"]["name"],
        "program_goal": master_json["program"]["goal"],
        "target_participants": master_json["program"]["target_participants"],
        "core_problem": master_json["program"]["core_problem"],
        "competency_focus": master_json["program"]["competency_focus"],
        "expected_outcomes": master_json["program"].get("expected_outcomes", []),
    }
    return _make_payload("bukti-2", context, [], ["organization_name", "program_name", "target_participants", "core_problem", "competency_focus"])


def _build_bukti_3_payload(master_json: dict[str, Any], *, fetch_json: Any) -> dict[str, Any]:
    unit_code = _selected_unit_code(master_json)
    mapping = _normalize_map_response(fetch_json(f"https://wsp.sertifikasitrainer.com/map/{unit_code}"))
    context = {
        "program_name": master_json["program"]["name"],
        "competency_focus": master_json["program"]["competency_focus"],
        "unit_code": unit_code,
        "map": mapping,
    }
    return _make_payload("bukti-3", context, ["skkni_map"], ["unit_code", "map.tujuanUtama", "map.fungsiKunci", "map.fungsiDasar"])


def _build_bukti_4_payload(master_json: dict[str, Any], *, fetch_json: Any) -> dict[str, Any]:
    unit_code = _selected_unit_code(master_json)
    detail = _normalize_unit_response(fetch_json(f"https://wsp.sertifikasitrainer.com/unit/{unit_code}"))
    context = {
        "unit_code": unit_code,
        "unit_detail": detail,
    }
    return _make_payload("bukti-4", context, ["skkni_unit_detail"], ["unit_code", "unit_detail.unitCode", "unit_detail.unitTitle", "unit_detail.elements"])


def _build_bukti_5_payload(master_json: dict[str, Any], *, fetch_json: Any) -> dict[str, Any]:
    context = {
        "program_name": master_json["program"]["name"],
        "target_participants": master_json["program"]["target_participants"],
        "delivery_evidence": master_json.get("delivery_evidence", {}),
    }
    return _make_payload("bukti-5", context, [], ["delivery_evidence.platform", "delivery_evidence.class_name", "delivery_evidence.assignment_examples"])


def _build_bukti_6_payload(master_json: dict[str, Any], *, fetch_json: Any) -> dict[str, Any]:
    context = {
        "organization": master_json["organization"],
        "program": master_json["program"],
        "training": master_json.get("training", {}),
    }
    return _make_payload("bukti-6", context, [], ["organization.name", "program.name", "program.goal", "program.target_participants"])


def _build_bukti_7_payload(master_json: dict[str, Any], *, fetch_json: Any) -> dict[str, Any]:
    context = {
        "program_name": master_json["program"]["name"],
        "partnership": master_json.get("partnership", {}),
    }
    return _make_payload("bukti-7", context, [], ["partnership.document_number", "partnership.agreement_date", "partnership.party_one", "partnership.party_two", "partnership.payment_terms"])


def _build_bukti_8_payload(master_json: dict[str, Any], *, fetch_json: Any) -> dict[str, Any]:
    context = {
        "program_name": master_json["program"]["name"],
        "evaluation_methods": master_json["program"].get("evaluation_methods", []),
        "evaluation_summary": master_json.get("evaluation_summary", {}),
    }
    return _make_payload("bukti-8", context, [], ["evaluation_summary.trainer_name", "evaluation_summary.participant_count", "evaluation_summary.feedback_count"])


def _make_payload(document_type: str, context: dict[str, Any], source_dependencies: list[str], required_inputs: list[str]) -> dict[str, Any]:
    missing_required_inputs = [field for field in required_inputs if _lookup(context, field) in (None, "", [], {})]
    return {
        "document_type": document_type,
        "context": context,
        "required_inputs": required_inputs,
        "optional_inputs": [],
        "missing_required_inputs": missing_required_inputs,
        "source_dependencies": source_dependencies,
        "generation_allowed": not missing_required_inputs,
    }


def _lookup(data: dict[str, Any], dotted_path: str) -> Any:
    current: Any = data
    for part in dotted_path.split("."):
        if isinstance(current, dict):
            current = current.get(part)
        else:
            return None
    return current


def _selected_unit_code(master_json: dict[str, Any]) -> str:
    codes = master_json.get("skkni", {}).get("selected_unit_codes", [])
    if not codes:
        raise ValueError("selected_unit_codes is required for bukti-3 and bukti-4")
    return codes[0]


def _format_duration(duration: dict[str, Any]) -> str:
    value = duration.get("value")
    unit = duration.get("unit", "hari")
    if value in (None, ""):
        return ""
    return f"{value} {unit}"


def _normalize_map_response(payload: dict[str, Any]) -> dict[str, Any]:
    if "competencyMapping" in payload:
        return payload.get("competencyMapping", {})
    return {
        "unitCode": payload.get("unit_code", ""),
        "tujuanUtama": payload.get("tujuan_utama", ""),
        "fungsiKunci": payload.get("fungsi_kunci", ""),
        "fungsiUtama": payload.get("fungsi_utama", "") or payload.get("sub_fungsi_utama", "") or "",
        "fungsiDasar": payload.get("fungsi_dasar", "") or payload.get("matched_fungsi_dasar", "") or "",
    }


def _normalize_unit_response(payload: dict[str, Any]) -> dict[str, Any]:
    if "unitDetails" in payload:
        return payload.get("unitDetails", {})
    data = payload.get("data", {})
    return {
        "unitCode": data.get("unit_code", ""),
        "unitTitle": data.get("unit_title", ""),
        "unitDescription": data.get("unit_description", ""),
        "elements": data.get("competency_elements", []),
        "performanceCriteria": [
            criteria
            for element in data.get("competency_elements", [])
            for criteria in element.get("performance_criteria", [])
        ],
        "requiredKnowledge": data.get("required_knowledge", []),
        "requiredSkills": data.get("required_skills", []),
        "workAttitudes": data.get("work_attitudes", []),
        "criticalAspects": data.get("critical_aspects", []),
        "assessmentContext": data.get("assessment_context", []),
        "variableConstraints": data.get("variable_constraints", {}),
    }


if __name__ == "__main__":
    main()
