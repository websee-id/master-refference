from __future__ import annotations

import argparse
import importlib
import json
from pathlib import Path
from typing import Any

from llma_pipeline.config import load_settings
from llma_pipeline.document_generation import build_document_payload, load_master_json


def build_json_system_prompt(document_type: str) -> str:
    return (
        f"Kamu adalah JSON payload composer untuk template Carbone dokumen {document_type}. "
        "Output harus JSON valid saja. Jangan output HTML. Jangan output markdown. "
        "Pertahankan field exact dari payload apa adanya. Isi field generated hanya pada area yang boleh AI-assisted. "
        "Jangan mengarang exact facts yang tidak ada di payload. Jika ada field exact yang kosong, biarkan kosong/null sesuai konteks schema."
    )


def build_json_user_prompt(document_type: str, payload: dict[str, Any]) -> str:
    return (
        f"Bentuk JSON payload final untuk template dokumen {document_type}. "
        "Gunakan payload berikut sebagai sumber utama. Pertahankan field exact, lalu lengkapi field naratif atau generated yang masuk akal untuk dokumen ini.\n\n"
        f"PAYLOAD:\n{json.dumps(payload, ensure_ascii=False)}"
    )


def generate_json_document(
    *,
    document_type: str,
    payload: dict[str, Any],
    settings: Any,
    client: Any | None = None,
) -> dict[str, Any]:
    active_client: Any
    generation_allowed = payload.get("generation_allowed")
    if generation_allowed is None:
        generation_allowed = not payload.get("missing_required_inputs", [])
    if not generation_allowed:
        raise ValueError(f"Cannot generate {document_type}; missing inputs: {payload.get('missing_required_inputs', [])}")

    if client is None:
        if not getattr(settings, "gemini_api_key", None):
            raise ValueError("Gemini API key is required for JSON generation")
        genai = importlib.import_module("google.genai")
        types = importlib.import_module("google.genai.types")
        active_client = genai.Client(api_key=settings.gemini_api_key)
        response = active_client.models.generate_content(
            model=settings.gemini_model,
            contents=build_json_user_prompt(document_type, payload),
            config=types.GenerateContentConfig(
                temperature=0,
                system_instruction=build_json_system_prompt(document_type),
                response_mime_type="application/json",
            ),
        )
    else:
        active_client = client
        response = active_client.models.generate_content(
            model=settings.gemini_model,
            contents=build_json_user_prompt(document_type, payload),
            config=None,
        )

    text = (response.text or "").strip()
    return json.loads(text)


def generate_all_document_jsons(
    *,
    master_json: dict[str, Any],
    settings: Any,
    output_dir: Path,
    document_types: list[str] | None = None,
) -> list[Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    for document_type in document_types or [f"bukti-{number}" for number in range(1, 9)]:
        payload = build_document_payload(document_type, master_json)
        generated = generate_json_document(document_type=document_type, payload=payload, settings=settings)
        out_path = output_dir / f"{document_type}.json"
        out_path.write_text(json.dumps(generated, ensure_ascii=False, indent=2), encoding="utf-8")
        written.append(out_path)
    return written


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate JSON payload dokumen from master JSON")
    parser.add_argument("--master-json", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, default=Path("generated-json"))
    parser.add_argument("--document-type", type=str)
    args = parser.parse_args()

    settings = load_settings()
    master_json = load_master_json(args.master_json)
    document_types = [args.document_type] if args.document_type else [f"bukti-{number}" for number in range(1, 9)]
    written = generate_all_document_jsons(
        master_json=master_json,
        settings=settings,
        output_dir=args.output_dir,
        document_types=document_types,
    )
    for path in written:
        print(path)


if __name__ == "__main__":
    main()
