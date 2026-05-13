import os
from pathlib import Path
import sys

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))


def load_streamlit_secrets_if_available() -> None:
    """
    Local development uses .env.
    Streamlit Cloud uses st.secrets.

    This function safely checks Streamlit secrets without crashing when
    .streamlit/secrets.toml does not exist locally.
    """
    try:
        secrets = dict(st.secrets)
    except Exception:
        secrets = {}

    for key in ["OPENAI_API_KEY", "OPENAI_MODEL", "LLM_PROVIDER"]:
        if key in secrets and secrets[key]:
            os.environ[key] = str(secrets[key])


load_streamlit_secrets_if_available()

from app.dashboard import main

if __name__ == "__main__":
    main()
