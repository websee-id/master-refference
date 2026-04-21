from __future__ import annotations

import html
from typing import Any


def validate_bukti_1_json(data: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if not data.get("document_title"):
        errors.append("document_title is required")
    if not data.get("program_title"):
        errors.append("program_title is required")
    if len(data.get("key_findings", [])) < 3:
        errors.append("key_findings must contain at least 3 items")
    if len(data.get("recommendations", [])) < 2:
        errors.append("recommendations must contain at least 2 items")
    if not data.get("introduction", {}).get("background"):
        errors.append("introduction.background is required")
    if not data.get("needs_analysis", {}).get("gap_analysis"):
        errors.append("needs_analysis.gap_analysis is required")
    if not data.get("conclusion"):
        errors.append("conclusion is required")
    return errors


def render_bukti_1_html(data: dict[str, Any]) -> str:
    errors = validate_bukti_1_json(data)
    if errors:
        raise ValueError(f"Invalid bukti-1 data: {errors}")

    title = html.escape(data.get("document_title", "TRAINING NEED ANALYSIS"))
    subtitle = html.escape(data.get("document_subtitle", ""))
    program_title = html.escape(data.get("program_title", ""))
    region = data.get("region_context", {})
    intro = data.get("introduction", {})
    comp = data.get("competency_reference", {})
    methodology = data.get("methodology", {})
    findings = data.get("key_findings", [])
    needs = data.get("needs_analysis", {})
    recommendations = data.get("recommendations", [])
    sign_off = data.get("sign_off", {})

    return f"""
<html>
  <head>
    <meta charset=\"utf-8\" />
    <title>{title}</title>
    <style>
      body {{ font-family: Arial, sans-serif; margin: 40px; color: #222; line-height: 1.6; }}
      h1, h2, h3 {{ margin-top: 24px; }}
      h1, h2 {{ text-align: center; }}
      table {{ width: 100%; border-collapse: collapse; margin-top: 12px; }}
      th, td {{ border: 1px solid #ccc; padding: 8px; vertical-align: top; }}
      ul {{ padding-left: 22px; }}
      .meta {{ margin-top: 12px; text-align: center; color: #555; }}
      .signature {{ margin-top: 40px; width: 100%; }}
    </style>
  </head>
  <body>
    <h1>{title}</h1>
    <h2>{subtitle}</h2>
    <div class="meta"><strong>{program_title}</strong></div>

    <h3>Pendahuluan</h3>
    <p>{html.escape(intro.get('background', ''))}</p>
    <p>{html.escape(intro.get('problem_statement', ''))}</p>
    <p>{html.escape(intro.get('training_objective', ''))}</p>

    <h3>Profil Wilayah</h3>
    <p><strong>Wilayah utama:</strong> {html.escape(region.get('primary_region', ''))}</p>
    <p><strong>Kota lembaga:</strong> {html.escape(region.get('organization_city', ''))}</p>
    <p><strong>Sektor:</strong> {html.escape(region.get('sector', ''))}</p>
    <p>{html.escape(region.get('generated_regional_profile', ''))}</p>
    <p>{html.escape(region.get('generated_business_landscape', ''))}</p>
    <p>{html.escape(region.get('generated_opportunity_summary', ''))}</p>

    <h3>Referensi Kompetensi</h3>
    <p><strong>Kode unit:</strong> {html.escape(comp.get('unit_code', ''))}</p>
    <p><strong>Judul unit:</strong> {html.escape(comp.get('unit_title', ''))}</p>
    <p>{html.escape(comp.get('summary', ''))}</p>

    <h3>Metodologi</h3>
    <p>{html.escape(methodology.get('approach_summary', ''))}</p>
    <table>
      <thead><tr><th>Metode</th><th>Deskripsi</th></tr></thead>
      <tbody>
        {''.join(f"<tr><td>{html.escape(item.get('name', ''))}</td><td>{html.escape(item.get('description', ''))}</td></tr>" for item in methodology.get('methods_used', []))}
      </tbody>
    </table>

    <h3>Temuan Utama</h3>
    <table>
      <thead><tr><th>Temuan</th><th>Uraian</th></tr></thead>
      <tbody>
        {''.join(f"<tr><td>{html.escape(item.get('title', ''))}</td><td>{html.escape(item.get('description', ''))}</td></tr>" for item in findings)}
      </tbody>
    </table>

    <h3>Analisis Kebutuhan</h3>
    <p>{html.escape(needs.get('current_condition', ''))}</p>
    <p>{html.escape(needs.get('gap_analysis', ''))}</p>
    <ul>
      {''.join(f"<li>{html.escape(item)}</li>" for item in needs.get('priority_needs', []))}
    </ul>

    <h3>Rekomendasi</h3>
    <table>
      <thead><tr><th>Rekomendasi</th><th>Uraian</th></tr></thead>
      <tbody>
        {''.join(f"<tr><td>{html.escape(item.get('title', ''))}</td><td>{html.escape(item.get('description', ''))}</td></tr>" for item in recommendations)}
      </tbody>
    </table>

    <h3>Kesimpulan</h3>
    <p>{html.escape(data.get('conclusion', ''))}</p>

    <div class="signature">
      <p>{html.escape(sign_off.get('city', ''))}, {html.escape(sign_off.get('date', ''))}</p>
      <p>Disiapkan oleh,</p>
      <br/><br/><br/>
      <p><strong>{html.escape(sign_off.get('prepared_by', ''))}</strong></p>
    </div>
  </body>
</html>
""".strip()
