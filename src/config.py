from __future__ import annotations

import os
from functools import lru_cache
from typing import Optional

from dotenv import load_dotenv

load_dotenv()


@lru_cache(maxsize=1)
def get_openai_api_key() -> Optional[str]:
    # 👉 1. STREAMLIT (produção)
    try:
        import streamlit as st
        if "OPENAI_API_KEY" in st.secrets:
            return str(st.secrets["OPENAI_API_KEY"])
    except Exception:
        pass

    # 👉 2. LOCAL (.env)
    key = os.getenv("OPENAI_API_KEY")
    if key:
        return key

    return None


def get_openai_model() -> str:
    try:
        import streamlit as st
        return st.secrets.get("OPENAI_MODEL", "gpt-4o-mini")
    except Exception:
        return os.getenv("OPENAI_MODEL", "gpt-4o-mini")


def openai_enabled() -> bool:
    return bool(get_openai_api_key())