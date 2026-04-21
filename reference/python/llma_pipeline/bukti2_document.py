from __future__ import annotations

import html
from typing import Any


def validate_bukti_2_json(data: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if not data.get("document_title"):
        errors.append("document_title is required")
    if not data.get("vision"):
        errors.append("vision is required")
    if len(data.get("mission", [])) < 2:
        errors.append("mission must contain at least 2 items")
    if len(data.get("sdm_analysis", {}).get("main_tasks", [])) < 3:
        errors.append("sdm_analysis.main_tasks must contain at least 3 items")
    if len(data.get("sdm_analysis", {}).get("performance_standards", [])) < 3:
        errors.append("sdm_analysis.performance_standards must contain at least 3 items")
    if len(data.get("training_recommendations", [])) < 2:
        errors.append("training_recommendations must contain at least 2 items")
    if not data.get("conclusion"):
        errors.append("conclusion is required")
    return errors


def render_bukti_2_html(data: dict[str, Any]) -> str:
    errors = validate_bukti_2_json(data)
    if errors:
        raise ValueError(f"Invalid bukti-2 data: {errors}")

    org = data.get("organization_profile", {})
    program = data.get("program_identity", {})
    sdm = data.get("sdm_analysis", {})
    comp = data.get("competency_needs_analysis", {})
    semester = data.get("semester_plan", {})
    recommendations = data.get("training_recommendations", [])
    sign = data.get("sign_off", {})

    return f"""
<html>
  <head>
    <meta charset=\"utf-8\" />
    <title>{html.escape(data.get('document_title', 'TRAINING NEED ANALYSIS'))}</title>
    <style>
      body {{ font-family: Arial, sans-serif; margin: 40px; color: #222; line-height: 1.6; }}
      h1, h2, h3 {{ margin-top: 24px; }}
      h1, h2 {{ text-align: center; }}
      table {{ width: 100%; border-collapse: collapse; margin: 16px 0; }}
      th, td {{ border: 1px solid #ccc; padding: 8px; vertical-align: top; }}
      ul {{ padding-left: 22px; }}
    </style>
  </head>
  <body>
    <h1>{html.escape(data.get('document_title', 'TRAINING NEED ANALYSIS'))}</h1>
    <h2>{html.escape(data.get('document_subtitle', 'TNA MIKRO'))}</h2>

    <p><strong>Training Need Analysis ditujukan untuk:</strong> {html.escape(org.get('organization_name', ''))}</p>
    <p>{html.escape(org.get('business_description', ''))}</p>

    <h3>Visi</h3>
    <p>{html.escape(data.get('vision', ''))}</p>

    <h3>Misi</h3>
    <ul>{''.join(f'<li>{html.escape(item)}</li>' for item in data.get('mission', []))}</ul>

    <h3>Analisa SDM</h3>
    <p><strong>Jabatan:</strong> {html.escape(sdm.get('position_name', ''))}</p>
    <p><strong>Fungsi:</strong> {html.escape(sdm.get('function', ''))}</p>
    <p><strong>Tugas Pokok:</strong></p>
    <ul>{''.join(f'<li>{html.escape(item)}</li>' for item in sdm.get('main_tasks', []))}</ul>
    <p><strong>Standar Kinerja (Capaian Pembelajaran):</strong></p>
    <ul>{''.join(f'<li>{html.escape(item)}</li>' for item in sdm.get('performance_standards', []))}</ul>

    <h3>Analisis Kebutuhan Kompetensi</h3>
    <p>{html.escape(comp.get('analysis_summary', ''))}</p>
    <p>{html.escape(comp.get('gap_description', ''))}</p>
    <ul>{''.join(f'<li>{html.escape(item)}</li>' for item in comp.get('priority_competencies', []))}</ul>

    <h3>Rencana Pembelajaran Semester</h3>
    <p>{html.escape(semester.get('description', ''))}</p>
    <table>
      <thead><tr><th>Minggu</th><th>Topik</th><th>Learning Outcome</th></tr></thead>
      <tbody>
        {''.join(f"<tr><td>{html.escape(item.get('week', ''))}</td><td>{html.escape(item.get('topic', ''))}</td><td>{html.escape(item.get('learning_outcome', ''))}</td></tr>" for item in semester.get('weekly_plan', []))}
      </tbody>
    </table>
    <p><strong>Referensi Utama:</strong></p>
    <ul>{''.join(f'<li>{html.escape(item)}</li>' for item in semester.get('main_references', []))}</ul>

    <h3>Rekomendasi Pelatihan</h3>
    <table>
      <thead><tr><th>Rekomendasi</th><th>Deskripsi</th></tr></thead>
      <tbody>
        {''.join(f"<tr><td>{html.escape(item.get('title', ''))}</td><td>{html.escape(item.get('description', ''))}</td></tr>" for item in recommendations)}
      </tbody>
    </table>

    <h3>Kesimpulan</h3>
    <p>{html.escape(data.get('conclusion', ''))}</p>

    <p>{html.escape(sign.get('city', ''))}, {html.escape(sign.get('date', ''))}</p>
    <p>Disiapkan oleh,</p>
    <br/><br/><br/>
    <p><strong>{html.escape(sign.get('prepared_by', ''))}</strong></p>
  </body>
</html>
""".strip()
