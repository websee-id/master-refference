from __future__ import annotations

import importlib
import json
from typing import Any


def build_bukti_7_system_prompt() -> str:
    return (
        "Kamu adalah JSON payload composer untuk template Carbone dokumen Bukti 7 (Draft PKS / MoU). "
        "Output harus JSON valid saja. Jangan output HTML. Jangan output markdown. "
        "Dokumen ini adalah legal draft template-driven, bukan final legal authoring engine. "
        "Wajib ada: party identities, opening_paragraph, premise_points, pasal_1_scope, pasal_2_execution, pasal_3_duration, pasal_4_cost, pasal_5_payment, pasal_6_obligations, dan closing_paragraph. "
        "Setiap pasal wajib punya field title dan content yang tidak kosong. "
        "Premise_points minimal 4 poin. Pasal biaya wajib menyebut nominal angka dan terbilang. "
        "Pertahankan exact identity fields. AI boleh membuat legal wording, boilerplate formal, dan struktur pasal."
    )


def build_bukti_7_prompt(payload: dict[str, Any]) -> str:
    return (
        "Bentuk JSON final untuk Bukti 7: draft PKS / MoU. "
        "Gunakan exact identity untuk party_one dan party_two dari payload, lalu susun premis dan pasal 1 sampai pasal 6 dalam gaya formal hukum yang rapi. "
        "Setiap pasal harus berupa object dengan {title, content}. Jangan gunakan format clauses. Jangan kosongkan content. "
        "Premis harus minimal 4 poin. Pasal biaya wajib menyebut nominal angka dan terbilang.\n\n"
        f"PAYLOAD:\n{json.dumps(payload, ensure_ascii=False)}"
    )


def generate_bukti_7_json(*, payload: dict[str, Any], settings: Any, client: Any | None = None) -> dict[str, Any]:
    active_client: Any
    generation_allowed = payload.get("generation_allowed")
    if generation_allowed is None:
        generation_allowed = not payload.get("missing_required_inputs", [])
    if not generation_allowed:
        raise ValueError(f"Cannot generate bukti-7; missing inputs: {payload.get('missing_required_inputs', [])}")

    if client is None:
        if not getattr(settings, "gemini_api_key", None):
            raise ValueError("Gemini API key is required for Bukti 7 generation")
        genai = importlib.import_module("google.genai")
        types = importlib.import_module("google.genai.types")
        active_client = genai.Client(api_key=settings.gemini_api_key)
        response = active_client.models.generate_content(
            model=settings.gemini_model,
            contents=build_bukti_7_prompt(payload),
            config=types.GenerateContentConfig(
                temperature=0,
                system_instruction=build_bukti_7_system_prompt(),
                response_mime_type="application/json",
            ),
        )
    else:
        active_client = client
        response = active_client.models.generate_content(
            model=settings.gemini_model,
            contents=build_bukti_7_prompt(payload),
            config=None,
        )

    raw = json.loads((response.text or "").strip())
    return normalize_bukti_7_json(raw)


def normalize_bukti_7_json(raw: dict[str, Any]) -> dict[str, Any]:
    agreement_location = raw.get("agreement_location", "")
    agreement_date = raw.get("agreement_date", "")
    party_one = raw.get("party_one", {})
    party_two = raw.get("party_two", {})
    return {
        "document_type": "bukti-7",
        "document_title": raw.get("document_title", "PERJANJIAN KERJASAMA"),
        "document_subtitle": raw.get("document_subtitle", ""),
        "document_number": raw.get("document_number", ""),
        "agreement_date": agreement_date,
        "agreement_location": agreement_location,
        "opening_paragraph": raw.get("opening_paragraph", f"Perjanjian Kerja Sama ini dibuat dan ditandatangani pada tanggal {agreement_date} di {agreement_location} oleh dan antara PARA PIHAK yang disebutkan di bawah ini."),
        "party_one": party_one,
        "party_two": party_two,
        "premise_points": raw.get("premise_points", []),
        "pasal_1_scope": _normalize_article(raw.get("pasal_1_scope") or raw.get("pasal_1", {}), _default_scope_content(party_one, party_two)),
        "pasal_2_execution": _normalize_article(raw.get("pasal_2_execution") or raw.get("pasal_2", {}), _default_execution_content()),
        "pasal_3_duration": _normalize_article(raw.get("pasal_3_duration") or raw.get("pasal_3", {}), _default_duration_content(agreement_date)),
        "pasal_4_cost": {
            **_normalize_article(raw.get("pasal_4_cost") or raw.get("pasal_4", {}), _default_cost_content()),
            "cost_estimate": (
                raw.get("pasal_4_cost", {}).get("cost_estimate")
                or _extract_cost_from_text((raw.get("pasal_4_cost") or {}).get("content", ""))
                or _extract_cost(raw.get("pasal_4", {}).get("clauses", []))
            ),
        },
        "pasal_5_payment": {
            **_normalize_article(raw.get("pasal_5_payment") or raw.get("pasal_5", {}), _default_payment_content()),
            "payment_terms": raw.get("pasal_5_payment", {}).get("payment_terms") or raw.get("payment_terms", "50% di muka dan 50% setelah pelatihan selesai"),
        },
        "pasal_6_obligations": _normalize_article(raw.get("pasal_6_obligations") or raw.get("pasal_6", {}), _default_obligations_content()),
        "closing_paragraph": raw.get("closing_paragraph", ""),
    }


def _normalize_article(article: dict[str, Any], fallback_content: str) -> dict[str, Any]:
    clauses = article.get("clauses", [])
    if isinstance(clauses, str):
        clauses = [clauses]
    content = article.get("content") or " ".join(item for item in clauses if item)
    return {
        "title": article.get("title", ""),
        "content": content or fallback_content,
    }


def _extract_cost(clauses: list[str]) -> int | None:
    for item in clauses:
        digits = ''.join(ch for ch in item if ch.isdigit())
        if digits:
            return int(digits)
    return None


def _extract_cost_from_text(text: str) -> int | None:
    digits = ''.join(ch for ch in text if ch.isdigit())
    return int(digits) if digits else None


def _default_scope_content(party_one: dict[str, Any], party_two: dict[str, Any]) -> str:
    return (
        f"PARA PIHAK sepakat bahwa ruang lingkup kerja sama ini meliputi penyelenggaraan program pelatihan yang dibutuhkan oleh {party_one.get('organization_name', 'PIHAK PERTAMA')} dan didukung pelaksanaannya oleh {party_two.get('organization_name', 'PIHAK KEDUA')} sesuai kesepakatan bersama."
    )


def _default_execution_content() -> str:
    return "Pelaksanaan pelatihan dilakukan sesuai jadwal, metode, dan ruang lingkup yang disepakati oleh PARA PIHAK dengan mengutamakan profesionalisme dan ketepatan pelaksanaan."


def _default_duration_content(agreement_date: str) -> str:
    return f"Perjanjian ini berlaku sejak tanggal {agreement_date} sampai seluruh kewajiban PARA PIHAK berdasarkan dokumen ini dinyatakan selesai."


def _default_cost_content() -> str:
    return "Biaya pelaksanaan program ditetapkan berdasarkan kesepakatan PARA PIHAK dan menjadi dasar pembayaran sebagaimana diatur lebih lanjut dalam pasal pembayaran."


def _default_payment_content() -> str:
    return "Pembayaran dilakukan sesuai termin dan mekanisme yang disepakati PARA PIHAK, dengan tetap memperhatikan ketentuan administratif yang berlaku."


def _default_obligations_content() -> str:
    return "PARA PIHAK berkewajiban melaksanakan seluruh kesepakatan dalam dokumen ini dengan itikad baik, profesional, dan sesuai tanggung jawab masing-masing."
