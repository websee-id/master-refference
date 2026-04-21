from __future__ import annotations

import html
from typing import Any


def validate_bukti_6_json(data: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if not data.get("document_title"):
        errors.append("document_title is required")
    if not data.get("executive_summary"):
        errors.append("executive_summary is required")
    if len(data.get("marketing_objectives", [])) < 3:
        errors.append("marketing_objectives must contain at least 3 items")
    if len(data.get("market_segments", [])) < 2:
        errors.append("market_segments must contain at least 2 items")
    if len(data.get("competitor_analysis", [])) < 2:
        errors.append("competitor_analysis must contain at least 2 items")
    if len(data.get("budget_breakdown", [])) < 3:
        errors.append("budget_breakdown must contain at least 3 items")
    if len(data.get("timeline", [])) < 3:
        errors.append("timeline must contain at least 3 items")
    if len(data.get("kpi", [])) < 3:
        errors.append("kpi must contain at least 3 items")
    if not data.get("conclusion"):
        errors.append("conclusion is required")
    if "evaluation_report" in data:
        errors.append("evaluation_report drift detected")
    return errors


def render_bukti_6_html(data: dict[str, Any]) -> str:
    errors = validate_bukti_6_json(data)
    if errors:
        raise ValueError(f"Invalid bukti-6 data: {errors}")

    identity = data.get("program_identity", {})
    return f"""
<html>
  <head>
    <meta charset=\"utf-8\" />
    <title>{html.escape(data.get('document_title', 'MARKETING PLAN'))}</title>
    <style>
      body {{ font-family: Arial, sans-serif; margin: 40px; color: #222; line-height: 1.6; }}
      h1, h2, h3 {{ margin-top: 24px; }}
      h1, h2 {{ text-align: center; }}
      table {{ width: 100%; border-collapse: collapse; margin: 16px 0; }}
      th, td {{ border: 1px solid #ccc; padding: 8px; vertical-align: top; }}
      ul {{ padding-left: 22px; }}
      .meta {{ margin-top: 12px; text-align: center; color: #555; }}
    </style>
  </head>
  <body>
    <h1>{html.escape(data.get('document_title', 'MARKETING PLAN'))}</h1>
    <div class="meta">
      <strong>{html.escape(identity.get('training_name', ''))}</strong><br/>
      {html.escape(identity.get('organization_name', ''))} - {html.escape(identity.get('organization_city', ''))}
    </div>

    <h2>Executive Summary</h2>
    <p>{html.escape(data.get('executive_summary', ''))}</p>

    <h2>Tujuan Pemasaran</h2>
    {_render_table(data.get('marketing_objectives', []))}

    <h2>Analisis Pasar</h2>
    <p><strong>Kondisi Pasar:</strong> {html.escape(data.get('market_analysis', {}).get('current_market_condition', ''))}</p>
    <p><strong>Target Market:</strong> {html.escape(data.get('market_analysis', {}).get('target_market_overview', ''))}</p>
    <p><strong>Masalah Konteks:</strong> {html.escape(data.get('market_analysis', {}).get('problem_context', ''))}</p>
    <p><strong>Peluang:</strong> {html.escape(data.get('market_analysis', {}).get('opportunity_analysis', ''))}</p>

    <h2>Segmentasi Pasar</h2>
    {_render_table(data.get('market_segments', []))}

    <h2>Analisis Pesaing</h2>
    {_render_table(data.get('competitor_analysis', []))}

    <h2>Value Proposition</h2>
    <p>{html.escape(data.get('value_proposition', {}).get('main_value', ''))}</p>
    <ul>{''.join(f'<li>{html.escape(item)}</li>' for item in data.get('value_proposition', {}).get('key_differentiators', []))}</ul>

    <h2>Strategi Pemasaran</h2>
    <p><strong>Product:</strong> {html.escape(data.get('marketing_strategy', {}).get('product_strategy', ''))}</p>
    <p><strong>Pricing:</strong> {html.escape(data.get('marketing_strategy', {}).get('pricing_strategy', ''))}</p>
    <p><strong>Promotion:</strong> {html.escape(data.get('marketing_strategy', {}).get('promotion_strategy', ''))}</p>
    <p><strong>Distribution:</strong> {html.escape(data.get('marketing_strategy', {}).get('distribution_strategy', ''))}</p>
    <p><strong>Communication:</strong> {html.escape(data.get('marketing_strategy', {}).get('communication_strategy', ''))}</p>

    <h2>Budget Breakdown</h2>
    {_render_table(data.get('budget_breakdown', []))}

    <h2>Timeline</h2>
    {_render_table(data.get('timeline', []))}

    <h2>KPI</h2>
    {_render_table(data.get('kpi', []))}

    <h2>Kesimpulan</h2>
    <p>{html.escape(data.get('conclusion', ''))}</p>
  </body>
</html>
""".strip()


def _render_table(rows: list[dict[str, Any]]) -> str:
    if not rows:
        return "<p>(Tidak ada data)</p>"
    headers = list(rows[0].keys())
    head_html = ''.join(f"<th>{html.escape(str(header).replace('_', ' ').title())}</th>" for header in headers)
    body_html = ''.join(
        f"<tr>{''.join(f'<td>{html.escape(str(row.get(header, '')))}</td>' for header in headers)}</tr>"
        for row in rows
    )
    return f"<table><thead><tr>{head_html}</tr></thead><tbody>{body_html}</tbody></table>"
