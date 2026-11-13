"""Compatibility entry point. The full main application/interface is app.py.
Preferred deployment: python -m streamlit run app.py
"""
from pathlib import Path
import runpy
runpy.run_path(str(Path(__file__).resolve().with_name('app.py')),run_name='__main__')
