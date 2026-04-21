from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Any, Callable
from urllib.request import Request, urlopen


API_URL = "https://apdf.io/api/pdf/file/create"


def build_apdf_payload(html: str) -> dict[str, Any]:
    return {
        "html": html,
        "format": "a4",
        "orientation": "portrait",
    }


def post_json(url: str, token: str, payload: dict[str, Any]) -> dict[str, Any]:
    request = Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/json",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    with urlopen(request) as response:
        return json.loads(response.read().decode("utf-8"))


def download_file(url: str, output_path: Path) -> None:
    request = Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urlopen(request) as response:
        output_path.write_bytes(response.read())


def create_pdf_from_html(
    *,
    html: str,
    api_token: str,
    post_json: Callable[[str, str, dict[str, Any]], dict[str, Any]] = post_json,
) -> dict[str, Any]:
    payload = build_apdf_payload(html)
    return post_json(API_URL, api_token, payload)


def convert_html_file_to_pdf(
    *,
    html_file: Path,
    output_pdf: Path,
    api_token: str,
    post_json: Callable[[str, str, dict[str, Any]], dict[str, Any]] = post_json,
    download_file: Callable[[str, Path], None] = download_file,
) -> dict[str, Any]:
    html = html_file.read_text(encoding="utf-8")
    result = create_pdf_from_html(html=html, api_token=api_token, post_json=post_json)
    output_pdf.parent.mkdir(parents=True, exist_ok=True)
    download_file(result["file"], output_pdf)
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description="Convert generated HTML files to A4 PDF using aPDF.io")
    parser.add_argument("--html-file", type=Path)
    parser.add_argument("--html-dir", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--output-dir", type=Path, default=Path("generated-pdf"))
    parser.add_argument("--api-token", type=str, default=os.getenv("APDF_API_TOKEN", ""))
    args = parser.parse_args()

    if not args.api_token:
        raise ValueError("APDF_API_TOKEN is required via --api-token or environment variable")

    if args.html_file:
        output = args.output or args.html_file.with_suffix(".pdf")
        result = convert_html_file_to_pdf(
            html_file=args.html_file,
            output_pdf=output,
            api_token=args.api_token,
        )
        print(json.dumps({"output": str(output), **result}, ensure_ascii=False, indent=2))
        return

    if args.html_dir:
        args.output_dir.mkdir(parents=True, exist_ok=True)
        for html_file in sorted(args.html_dir.glob("*.html")):
            output = args.output_dir / f"{html_file.stem}.pdf"
            result = convert_html_file_to_pdf(
                html_file=html_file,
                output_pdf=output,
                api_token=args.api_token,
            )
            print(json.dumps({"output": str(output), **result}, ensure_ascii=False))
        return

    raise ValueError("Provide either --html-file or --html-dir")


if __name__ == "__main__":
    main()
