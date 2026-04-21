from __future__ import annotations

import html
from typing import Any


def validate_bukti_7_json(data: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if not data.get("document_title"):
        errors.append("document_title is required")
    if not data.get("party_one", {}).get("organization_name"):
        errors.append("party_one.organization_name is required")
    if not data.get("party_two", {}).get("organization_name"):
        errors.append("party_two.organization_name is required")
    if len(data.get("premise_points", [])) < 4:
        errors.append("premise_points must contain at least 4 items")
    for key in [
        "pasal_1_scope",
        "pasal_2_execution",
        "pasal_3_duration",
        "pasal_4_cost",
        "pasal_5_payment",
        "pasal_6_obligations",
    ]:
        if not data.get(key, {}).get("content"):
            errors.append(f"{key}.content is required")
    if data.get("pasal_4_cost", {}).get("cost_estimate") in (None, 0):
        errors.append("pasal_4_cost.cost_estimate is required")
    if not data.get("closing_paragraph"):
        errors.append("closing_paragraph is required")
    return errors


def render_bukti_7_html(data: dict[str, Any]) -> str:
    errors = validate_bukti_7_json(data)
    if errors:
        raise ValueError(f"Invalid bukti-7 data: {errors}")

    party_one = data.get("party_one", {})
    party_two = data.get("party_two", {})
    return f"""
<html>
  <head>
    <meta charset=\"utf-8\" />
    <title>{html.escape(data.get('document_title', 'PERJANJIAN KERJASAMA'))}</title>
    <style>
      body {{ font-family: Arial, sans-serif; margin: 40px; color: #222; line-height: 1.7; }}
      h1, h2, h3 {{ margin-top: 24px; text-align: center; }}
      ul {{ padding-left: 24px; }}
      .center {{ text-align: center; }}
    </style>
  </head>
  <body>
    <h1>{html.escape(data.get('document_title', 'PERJANJIAN KERJASAMA'))}</h1>
    <h2>{html.escape(data.get('document_subtitle', ''))}</h2>
    <p class="center">No. {html.escape(data.get('document_number', ''))}</p>
    <p class="center">Pada tanggal {html.escape(data.get('agreement_date', ''))} di {html.escape(data.get('agreement_location', ''))}</p>
    <p>{html.escape(data.get('opening_paragraph', ''))}</p>

    <p><strong>PIHAK PERTAMA:</strong> {html.escape(party_one.get('organization_name', ''))}, diwakili oleh {html.escape(party_one.get('representative_name', ''))}, {html.escape(party_one.get('representative_title', ''))}, beralamat di {html.escape(party_one.get('address', ''))}.</p>
    <p><strong>PIHAK KEDUA:</strong> {html.escape(party_two.get('organization_name', ''))}, diwakili oleh {html.escape(party_two.get('representative_name', ''))}, {html.escape(party_two.get('representative_title', ''))}, beralamat di {html.escape(party_two.get('address', ''))}.</p>

    <h3>PARA PIHAK terlebih dahulu menerangkan:</h3>
    <ul>{''.join(f'<li>{html.escape(item)}</li>' for item in data.get('premise_points', []))}</ul>

    {_render_article('PASAL 1', data.get('pasal_1_scope', {}))}
    {_render_article('PASAL 2', data.get('pasal_2_execution', {}))}
    {_render_article('PASAL 3', data.get('pasal_3_duration', {}))}
    {_render_article('PASAL 4', data.get('pasal_4_cost', {}))}
    {_render_article('PASAL 5', data.get('pasal_5_payment', {}))}
    {_render_article('PASAL 6', data.get('pasal_6_obligations', {}))}

    <p>{html.escape(data.get('closing_paragraph', ''))}</p>
  </body>
</html>
""".strip()


def _render_article(label: str, article: dict[str, Any]) -> str:
    return f"<h3>{html.escape(label)}</h3><p><strong>{html.escape(article.get('title', ''))}</strong></p><p>{html.escape(article.get('content', ''))}</p>"
