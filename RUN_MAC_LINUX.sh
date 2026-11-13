#!/usr/bin/env sh
set -eu
cd "$(dirname "$0")"
python3.13 --version
[ -x .venv/bin/python ] || python3.13 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
exec .venv/bin/python -m streamlit run app.py
