from __future__ import annotations

import importlib
import json
from typing import Any


def build_bukti_6_system_prompt() -> str:
    return (
        "Kamu adalah JSON payload composer untuk template Carbone dokumen Bukti 6 (Marketing Plan). "
        "Output harus JSON valid saja. Jangan output HTML. Jangan output markdown. "
        "Dokumen harus berupa marketing plan yang panjang, strategis, dan realistis untuk konteks pelatihan di Indonesia. "
        "Wajib ada: executive summary, marketing objectives, market analysis, market segments, competitor analysis, value proposition, marketing strategy, budget breakdown, timeline, KPI, conclusion. "
        "Jangan menghasilkan evaluation report. Jangan membuat outline pendek."
    )


def build_bukti_6_prompt(payload: dict[str, Any]) -> str:
    return (
        "Bentuk JSON final untuk Bukti 6: Marketing Plan. "
        "Gunakan payload sebagai sumber fakta exact, lalu isi section pemasaran secara kaya dan realistis. "
        "Wajib ada executive summary, market analysis, market segments, competitor analysis, value proposition, marketing strategy, budget breakdown, timeline, dan KPI.\n\n"
        f"PAYLOAD:\n{json.dumps(payload, ensure_ascii=False)}"
    )


def generate_bukti_6_json(*, payload: dict[str, Any], settings: Any, client: Any | None = None) -> dict[str, Any]:
    active_client: Any
    generation_allowed = payload.get("generation_allowed")
    if generation_allowed is None:
        generation_allowed = not payload.get("missing_required_inputs", [])
    if not generation_allowed:
        raise ValueError(f"Cannot generate bukti-6; missing inputs: {payload.get('missing_required_inputs', [])}")

    if client is None:
        if not getattr(settings, "gemini_api_key", None):
            raise ValueError("Gemini API key is required for Bukti 6 generation")
        genai = importlib.import_module("google.genai")
        types = importlib.import_module("google.genai.types")
        active_client = genai.Client(api_key=settings.gemini_api_key)
        response = active_client.models.generate_content(
            model=settings.gemini_model,
            contents=build_bukti_6_prompt(payload),
            config=types.GenerateContentConfig(
                temperature=0,
                system_instruction=build_bukti_6_system_prompt(),
                response_mime_type="application/json",
            ),
        )
    else:
        active_client = client
        response = active_client.models.generate_content(
            model=settings.gemini_model,
            contents=build_bukti_6_prompt(payload),
            config=None,
        )

    raw = json.loads((response.text or "").strip())
    return normalize_bukti_6_json(raw, payload)


def normalize_bukti_6_json(raw: dict[str, Any], payload: dict[str, Any]) -> dict[str, Any]:
    context = payload.get("context", {})
    organization = context.get("organization", {})
    program = context.get("program", {})
    training = context.get("training", {})

    objectives = raw.get("marketing_objectives", [])
    if objectives and isinstance(objectives[0], str):
        objectives = [
            {"objective": item, "target_metric": "", "timeframe": ""}
            for item in objectives
        ]
    while len(objectives) < 3:
        defaults = [
            {"objective": "Meningkatkan awareness program", "target_metric": "Reach meningkat 30%", "timeframe": "3 bulan"},
            {"objective": "Menghasilkan leads berkualitas", "target_metric": "50 prospek", "timeframe": "6 bulan"},
            {"objective": "Meningkatkan konversi pendaftaran", "target_metric": "20 peserta", "timeframe": "6 bulan"},
        ]
        objectives.append(defaults[len(objectives)])

    market_analysis = raw.get("market_analysis", {})
    if isinstance(market_analysis, str):
        market_analysis = {
            "current_market_condition": market_analysis,
            "target_market_overview": f"Target pasar utama program ini adalah {program.get('target_participants', '')} yang membutuhkan solusi atas masalah {program.get('core_problem', '')}.",
            "problem_context": program.get("core_problem", ""),
            "opportunity_analysis": f"Peluang pasar terbuka karena kebutuhan terhadap {training.get('name', program.get('name', 'program pelatihan'))} masih tinggi dan dapat diperluas melalui kanal digital yang sesuai dengan konteks {organization.get('city', '')}.",
        }

    value_prop = raw.get("value_proposition", {})
    if isinstance(value_prop, str):
        value_prop = {
            "main_value": value_prop,
            "key_differentiators": [value_prop],
        }

    marketing_strategy = raw.get("marketing_strategy", {})
    if isinstance(marketing_strategy, list):
        strategy_map = {str(item.get("strategy", "")).lower(): item for item in marketing_strategy if isinstance(item, dict)}
        promotion_parts = []
        for item in marketing_strategy:
            if isinstance(item, dict):
                channel = item.get("channel", "")
                strategy = item.get("strategy", "")
                tactics = item.get("tactics", "")
                promotion_parts.append(f"{channel} - {strategy}: {tactics}".strip())
        marketing_strategy = {
            "product_strategy": strategy_map.get("edukasi dan awareness", {}).get("tactics", "") or strategy_map.get("product", {}).get("tactics", ""),
            "pricing_strategy": raw.get("pricing_strategy", "Value-based pricing untuk segmen UMKM dengan titik harga terjangkau namun tetap mencerminkan nilai program."),
            "promotion_strategy": " ".join(part for part in promotion_parts if part).strip(),
            "distribution_strategy": raw.get("distribution_strategy", "Distribusi dilakukan secara digital melalui landing page, webinar, dan kemitraan komunitas."),
            "communication_strategy": raw.get("communication_strategy", "Komunikasi pemasaran menekankan solusi atas masalah iklan boros dan peningkatan penjualan yang terukur."),
        }
    marketing_strategy = {
        "product_strategy": marketing_strategy.get("product_strategy") or marketing_strategy.get("product", ""),
        "pricing_strategy": marketing_strategy.get("pricing_strategy") or marketing_strategy.get("price", ""),
        "promotion_strategy": marketing_strategy.get("promotion_strategy") or marketing_strategy.get("promotion", ""),
        "distribution_strategy": marketing_strategy.get("distribution_strategy") or marketing_strategy.get("place", ""),
        "communication_strategy": marketing_strategy.get("communication_strategy") or marketing_strategy.get("promotion", ""),
    }

    budget = []
    for item in raw.get("budget_breakdown", []):
        amount = item.get("amount_idr")
        cost_text = item.get("amount") or item.get("cost")
        if amount is None and isinstance(cost_text, str):
            digits = ''.join(ch for ch in cost_text if ch.isdigit())
            amount = int(digits) if digits else 0
        budget.append(
            {
                "item": item.get("item", ""),
                "amount_idr": amount or 0,
                "description": item.get("description") or item.get("notes", ""),
            }
        )
    if len(budget) < 3:
        budget.extend([
            {"item": "Iklan Digital", "amount_idr": 10000000, "description": "Distribusi iklan untuk awareness dan lead generation"},
            {"item": "Produksi Konten", "amount_idr": 5000000, "description": "Pembuatan materi promosi, desain, dan copywriting"},
            {"item": "Aktivasi Komunitas", "amount_idr": 3000000, "description": "Kolaborasi komunitas dan webinar promosi"},
        ][len(budget):])

    timeline = [
        {
            "phase": item.get("phase", ""),
            "activity": item.get("activity") or item.get("activities", ""),
            "period": item.get("period", ""),
        }
        for item in raw.get("timeline", [])
    ]
    if len(timeline) < 3:
        timeline.extend([
            {"phase": "Fase 1", "activity": "Campaign awareness", "period": "Bulan 1-2"},
            {"phase": "Fase 2", "activity": "Lead generation", "period": "Bulan 3-4"},
            {"phase": "Fase 3", "activity": "Conversion push", "period": "Bulan 5-6"},
        ][len(timeline):])

    kpi = [
        {
            "name": item.get("name") or item.get("metric", ""),
            "target": item.get("target", ""),
            "measurement": item.get("measurement", ""),
        }
        for item in raw.get("kpi", [])
    ]
    if len(kpi) < 3:
        kpi.extend([
            {"name": "Reach", "target": "30% increase", "measurement": "Platform analytics"},
            {"name": "Leads", "target": "50 qualified leads", "measurement": "Lead form / contact entries"},
            {"name": "Registrations", "target": "20 peserta", "measurement": "Confirmed registrations"},
        ][len(kpi):])

    key_differentiators = value_prop.get("key_differentiators", [])
    if isinstance(key_differentiators, str):
        key_differentiators = [key_differentiators]
    elif not key_differentiators:
        key_differentiators = [value_prop.get("main_value", "")]

    return {
        "document_type": "bukti-6",
        "document_title": "MARKETING PLAN",
        "program_identity": {
            "program_name": raw.get("program_name", program.get("name", "")),
            "training_name": raw.get("training_name", training.get("name", "")),
            "organization_name": raw.get("organization_name", organization.get("name", "")),
            "organization_city": raw.get("location", organization.get("city", "")),
            "sector": organization.get("sector", program.get("field", "")),
            "target_participants": raw.get("target_participants", program.get("target_participants", "")),
            "delivery_method": raw.get("delivery_method", program.get("delivery_method", "")),
            "duration": raw.get("duration", f"{program.get('duration', {}).get('value', '')} {program.get('duration', {}).get('unit', '')}".strip()),
        },
        "executive_summary": raw.get("executive_summary", ""),
        "marketing_objectives": objectives,
        "market_analysis": market_analysis,
        "market_segments": _ensure_market_segments(raw.get("market_segments", [])),
        "competitor_analysis": _ensure_competitor_analysis(raw.get("competitor_analysis", [])),
        "value_proposition": {
            "main_value": value_prop.get("main_value", ""),
            "key_differentiators": [item for item in key_differentiators if item],
        },
        "marketing_strategy": marketing_strategy,
        "budget_breakdown": budget,
        "timeline": timeline,
        "kpi": kpi,
        "conclusion": raw.get("conclusion", ""),
        "sign_off": {
            "prepared_by": context.get("trainer_name", "Trainer Utama"),
            "city": organization.get("city", ""),
            "date": "21 April 2026",
        },
    }


def _ensure_market_segments(segments: list[dict[str, Any]]) -> list[dict[str, Any]]:
    normalized = list(segments)
    defaults = [
        {"segment_name": "UMKM Kuliner", "description": "Pemilik usaha makanan dan minuman yang aktif memasarkan produk secara digital.", "needs": "Butuh strategi promosi hemat biaya namun tetap menjangkau pasar luas."},
        {"segment_name": "UMKM Fashion", "description": "Pelaku usaha fashion yang bergantung pada visual dan engagement media sosial.", "needs": "Membutuhkan peningkatan awareness dan konversi penjualan melalui iklan digital."},
        {"segment_name": "UMKM Retail Lokal", "description": "Usaha retail dengan pasar lokal yang ingin memperluas penjualan melalui kanal digital.", "needs": "Perlu strategi targeting, promosi, dan retargeting yang lebih efektif."},
    ]
    while len(normalized) < 3:
        normalized.append(defaults[len(normalized)])
    return normalized


def _ensure_competitor_analysis(competitors: list[dict[str, Any]]) -> list[dict[str, Any]]:
    normalized = list(competitors)
    defaults = [
        {"competitor_name": "Lembaga Pelatihan Digital Lokal", "strengths": "Memiliki jaringan komunitas lokal yang kuat.", "weaknesses": "Belum menawarkan pendekatan yang terstruktur dan berbasis data.", "positioning_gap": "Program ini dapat menonjolkan pendekatan strategis dan pengukuran hasil."},
        {"competitor_name": "Kursus Online Umum", "strengths": "Harga terjangkau dan akses luas.", "weaknesses": "Kurang kontekstual untuk kebutuhan UMKM Indonesia.", "positioning_gap": "Program ini dapat fokus pada studi kasus lokal dan implementasi nyata."},
    ]
    while len(normalized) < 2:
        normalized.append(defaults[len(normalized)])
    return normalized
