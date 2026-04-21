from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import os


@dataclass(frozen=True)
class Settings:
    llama_cloud_api_key: str
    postgres_url: str
    workspace_root: Path
    parse_tier: str = "cost_effective"
    parse_version: str = "latest"
    gemini_api_key: str | None = None
    gemini_model: str = "gemini-3.1-pro-preview"


def load_settings(env_path: Path | None = None) -> Settings:
    env_path = env_path or Path(".env")
    explicit: dict[str, str] = {}
    fallback_values: list[str] = []

    if env_path.exists():
        for raw_line in env_path.read_text(encoding="utf-8").splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line and line.split("=", 1)[0].replace("_", "").isalnum():
                key, value = line.split("=", 1)
                explicit[key.strip()] = value.strip()
            else:
                fallback_values.append(line)

    llama_key = (
        os.getenv("LLAMA_CLOUD_API_KEY")
        or explicit.get("LLAMA_CLOUD_API_KEY")
        or next((value for value in fallback_values if value.startswith("llx-")), "")
    )
    postgres_url = (
        os.getenv("POSTGRES_URL")
        or os.getenv("DATABASE_URL")
        or explicit.get("POSTGRES_URL")
        or explicit.get("DATABASE_URL")
        or next((value for value in fallback_values if value.startswith("postgresql://")), "")
    )
    parse_tier = (
        os.getenv("LLAMA_PARSE_TIER")
        or explicit.get("LLAMA_PARSE_TIER")
        or "cost_effective"
    )
    parse_version = (
        os.getenv("LLAMA_PARSE_VERSION")
        or explicit.get("LLAMA_PARSE_VERSION")
        or "latest"
    )
    gemini_api_key = (
        os.getenv("GEMINI_API_KEY")
        or explicit.get("GEMINI_API_KEY")
        or next(
            (
                value.split(":", 1)[1].strip()
                for value in fallback_values
                if value.lower().startswith("gemini:")
            ),
            None,
        )
    )
    gemini_model = (
        os.getenv("GEMINI_MODEL")
        or explicit.get("GEMINI_MODEL")
        or "gemini-3.1-pro-preview"
    )

    if not llama_key:
        raise ValueError("Could not locate LLAMA_CLOUD_API_KEY in environment or .env file")
    if not postgres_url:
        raise ValueError("Could not locate Postgres connection URL in environment or .env file")

    return Settings(
        llama_cloud_api_key=llama_key,
        postgres_url=postgres_url,
        workspace_root=env_path.resolve().parent,
        parse_tier=parse_tier,
        parse_version=parse_version,
        gemini_api_key=gemini_api_key,
        gemini_model=gemini_model,
    )
