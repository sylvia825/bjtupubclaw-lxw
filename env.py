import os
from pathlib import Path
from typing import Dict, Optional


def _first_non_empty(*values: Optional[str]) -> Optional[str]:
    for value in values:
        if value is not None and str(value).strip() != "":
            return str(value).strip()
    return None


def load_env_file(env_path: Optional[str] = None) -> Optional[Path]:
    candidates = []
    if env_path:
        candidates.append(Path(env_path))
    else:
        env_file = os.environ.get("ENV_FILE")
        if env_file:
            candidates.append(Path(env_file))
        here = Path(__file__).resolve().parent
        # Prefer package .env to avoid picking up unrelated CWD .env when running as module
        candidates.append(here / ".env")
        candidates.append(here.parent / ".env")
        candidates.append(Path.cwd() / ".env")
    dedup = []
    for path in candidates:
        if path not in dedup:
            dedup.append(path)
    target = next((path for path in dedup if path.exists()), None)
    if not target:
        return None
    encodings = ["utf-8", "utf-8-sig", "utf-16", "utf-16-le", "utf-16-be"]
    for encoding in encodings:
        try:
            with open(target, "r", encoding=encoding) as f:
                for raw_line in f:
                    line = raw_line.strip()
                    if not line or line.startswith("#") or "=" not in line:
                        continue
                    key, value = line.split("=", 1)
                    key = key.strip().lstrip("\ufeff")
                    if key.startswith("export "):
                        key = key[7:].strip()
                    value = value.strip().strip('"').strip("'")
                    if key and (key not in os.environ or str(os.environ.get(key, "")).strip() == ""):
                        os.environ[key] = value
            return target
        except Exception:
            continue
    return target


def apply_aliases() -> Dict[str, str]:
    # Prefer provider-specific keys if present, then fall back to generic OPENAI_* or existing engine keys
    source_key = _first_non_empty(
        os.environ.get("KIMI_API_KEY"),
        os.environ.get("QWEN_API_KEY"),
        os.environ.get("DASHSCOPE_API_KEY"),
        os.environ.get("OPENAI_API_KEY"),
        os.environ.get("INSIGHT_ENGINE_API_KEY"),
        os.environ.get("REPORT_ENGINE_API_KEY"),
        os.environ.get("QUERY_ENGINE_API_KEY"),
    )
    source_base = _first_non_empty(
        os.environ.get("KIMI_BASE_URL"),
        os.environ.get("QWEN_BASE_URL"),
        os.environ.get("OPENAI_BASE_URL"),
    )
    source_model = _first_non_empty(
        os.environ.get("KIMI_MODEL_NAME"),
        os.environ.get("KIMI_MODEL"),
        os.environ.get("QWEN_MODEL_NAME"),
        os.environ.get("QWEN_MODEL"),
    )
    if not source_base and _first_non_empty(os.environ.get("QWEN_API_KEY"), os.environ.get("DASHSCOPE_API_KEY")):
        source_base = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    if not source_model and _first_non_empty(os.environ.get("QWEN_API_KEY"), os.environ.get("DASHSCOPE_API_KEY")):
        source_model = "qwen-plus"
    if not source_base and os.environ.get("KIMI_API_KEY"):
        source_base = "https://api.moonshot.cn/v1"
    if not source_model and os.environ.get("KIMI_API_KEY"):
        source_model = "moonshot-v1-8k"
    if source_key:
        os.environ.setdefault("OPENAI_API_KEY", source_key)
        os.environ.setdefault("INSIGHT_ENGINE_API_KEY", source_key)
        os.environ.setdefault("REPORT_ENGINE_API_KEY", source_key)
        os.environ.setdefault("QUERY_ENGINE_API_KEY", source_key)
    if source_base:
        os.environ.setdefault("OPENAI_BASE_URL", source_base)
        os.environ.setdefault("INSIGHT_ENGINE_BASE_URL", source_base)
        os.environ.setdefault("REPORT_ENGINE_BASE_URL", source_base)
        os.environ.setdefault("QUERY_ENGINE_BASE_URL", source_base)
    if source_model:
        os.environ.setdefault("INSIGHT_ENGINE_MODEL_NAME", source_model)
        os.environ.setdefault("REPORT_ENGINE_MODEL_NAME", source_model)
        os.environ.setdefault("QUERY_ENGINE_MODEL_NAME", source_model)
    return {
        "OPENAI_API_KEY": "set" if os.environ.get("OPENAI_API_KEY") else "empty",
        "INSIGHT_ENGINE_API_KEY": "set" if os.environ.get("INSIGHT_ENGINE_API_KEY") else "empty",
        "REPORT_ENGINE_API_KEY": "set" if os.environ.get("REPORT_ENGINE_API_KEY") else "empty",
        "QUERY_ENGINE_API_KEY": "set" if os.environ.get("QUERY_ENGINE_API_KEY") else "empty",
        "INSIGHT_ENGINE_BASE_URL": os.environ.get("INSIGHT_ENGINE_BASE_URL", ""),
        "REPORT_ENGINE_BASE_URL": os.environ.get("REPORT_ENGINE_BASE_URL", ""),
        "QUERY_ENGINE_BASE_URL": os.environ.get("QUERY_ENGINE_BASE_URL", ""),
        "INSIGHT_ENGINE_MODEL_NAME": os.environ.get("INSIGHT_ENGINE_MODEL_NAME", ""),
        "REPORT_ENGINE_MODEL_NAME": os.environ.get("REPORT_ENGINE_MODEL_NAME", ""),
        "QUERY_ENGINE_MODEL_NAME": os.environ.get("QUERY_ENGINE_MODEL_NAME", ""),
    }


def bootstrap_env() -> Dict[str, str]:
    load_env_file()
    return apply_aliases()
