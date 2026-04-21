from __future__ import annotations

import argparse
import html
import json
from pathlib import Path
from typing import Any, Callable

from llma_pipeline.apdf_pdf import convert_html_file_to_pdf
from llma_pipeline.config import load_settings
from llma_pipeline.document_json_generation import generate_all_document_jsons
from llma_pipeline.document_generation import load_master_json


def render_json_to_html(document_type: str, data: dict[str, Any]) -> str:
    title = data.get("document_title") or data.get("title") or document_type.upper()
    body = _render_value(data)
    return f"<html><head><meta charset='utf-8'><title>{html.escape(title)}</title><style>{_base_css()}</style></head><body><h1>{html.escape(title)}</h1>{body}</body></html>"


def run_json_to_pdf_pipeline(
    *,
    master_json_file: Path,
    output_json_dir: Path,
    output_html_dir: Path,
    output_pdf_dir: Path,
    settings: Any,
    api_token: str,
    document_types: list[str] | None = None,
    generate_jsons: Callable[..., list[Path]] = generate_all_document_jsons,
    convert_html_to_pdf: Callable[..., dict[str, Any]] = convert_html_file_to_pdf,
) -> list[dict[str, Any]]:
    master_json = load_master_json(master_json_file)
    document_types = document_types or [f"bukti-{number}" for number in range(1, 9)]
    json_paths = generate_jsons(
        master_json=master_json,
        settings=settings,
        output_dir=output_json_dir,
        document_types=document_types,
    )

    output_html_dir.mkdir(parents=True, exist_ok=True)
    output_pdf_dir.mkdir(parents=True, exist_ok=True)
    results: list[dict[str, Any]] = []
    for json_path in json_paths:
        document_type = json_path.stem
        data = json.loads(json_path.read_text(encoding="utf-8"))
        html_output = output_html_dir / f"{document_type}.html"
        pdf_output = output_pdf_dir / f"{document_type}.pdf"
        html_output.write_text(render_json_to_html(document_type, data), encoding="utf-8")
        pdf_result = convert_html_to_pdf(
            html_file=html_output,
            output_pdf=pdf_output,
            api_token=api_token,
        )
        results.append(
            {
                "document_type": document_type,
                "json_file": str(json_path),
                "html_file": str(html_output),
                "pdf_file": str(pdf_output),
                **pdf_result,
            }
        )
    return results


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate JSON, HTML, and PDF bukti documents end-to-end")
    parser.add_argument("--master-json", type=Path, required=True)
    parser.add_argument("--output-json-dir", type=Path, default=Path("generated-json"))
    parser.add_argument("--output-html-dir", type=Path, default=Path("generated-html"))
    parser.add_argument("--output-pdf-dir", type=Path, default=Path("generated-pdf"))
    parser.add_argument("--document-type", type=str)
    parser.add_argument("--api-token", type=str, required=True)
    args = parser.parse_args()

    settings = load_settings()
    document_types = [args.document_type] if args.document_type else None
    results = run_json_to_pdf_pipeline(
        master_json_file=args.master_json,
        output_json_dir=args.output_json_dir,
        output_html_dir=args.output_html_dir,
        output_pdf_dir=args.output_pdf_dir,
        settings=settings,
        api_token=args.api_token,
        document_types=document_types,
    )
    print(json.dumps(results, ensure_ascii=False, indent=2))


def _render_value(value: Any, level: int = 2) -> str:
    if isinstance(value, dict):
        parts = []
        for key, child in value.items():
            label = html.escape(key.replace("_", " ").title())
            if isinstance(child, (dict, list)):
                parts.append(f"<h{min(level,6)}>{label}</h{min(level,6)}>{_render_value(child, level + 1)}")
            else:
                parts.append(f"<p><strong>{label}:</strong> {html.escape(str(child))}</p>")
        return ''.join(parts)
    if isinstance(value, list):
        if value and all(isinstance(item, dict) for item in value):
            rows = []
            headers = list(value[0].keys())
            head_html = ''.join(f"<th>{html.escape(str(header).replace('_', ' ').title())}</th>" for header in headers)
            for item in value:
                row_html = ''.join(f"<td>{html.escape(str(item.get(header, '')))}</td>" for header in headers)
                rows.append(f"<tr>{row_html}</tr>")
            return f"<table><thead><tr>{head_html}</tr></thead><tbody>{''.join(rows)}</tbody></table>"
        return f"<ul>{''.join(f'<li>{html.escape(str(item))}</li>' for item in value)}</ul>"
    return f"<p>{html.escape(str(value))}</p>"


def _base_css() -> str:
    return "body{font-family:Arial,sans-serif;margin:32px;color:#222}h1,h2,h3,h4{margin-top:24px}table{border-collapse:collapse;width:100%;margin:16px 0}th,td{border:1px solid #ccc;padding:8px;vertical-align:top}ul{padding-left:20px}"


if __name__ == "__main__":
    main()
