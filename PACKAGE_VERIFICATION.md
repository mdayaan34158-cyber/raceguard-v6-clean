# RaceGuard Streamlit v6 — package verification

## Main application and interface
- `app.py` is the full main native Streamlit UI implementation, not a launcher. `streamlit_app.py` is a compatibility alias.
- Run `python -m streamlit run app.py`; deploy with main file `app.py` and the complete project contents.
- RaceGuard dark/slate/mint styling, branded sidebar, heroes, KPI cards and illustrative bearing are bundled in `assets/raceguard.css` and `src/presentation.py`. Native Streamlit widgets remain; no pixel-identical HTML dashboard claim.

## Executed checks
- Fresh isolated Python 3.13 environment: dependency installation, pip check and source compilation passed; no active Gradio/Flask installation.
- Working source: 69 Python tests, 15 functional Chromium workflows and 5 visual/browser checks passed.
- Staging ZIP extracted into a separate directory: CRC and every SHA256SUMS entry verified. Extracted `app.py` started separately on port 8502. All **69 tests passed in 9.69 seconds**, plus **15 functional and 5 visual/browser checks passed** against that server, with zero JavaScript page errors and no displayed Streamlit exception.
- Extracted-browser coverage includes actual classifier results, current/history, CSV upload, synthetic signal-only behavior, input errors, RUL, WAV/logs, virtual microphone Record→Stop→Analyse→export, downloads, visible bearing-image decoding and 390px responsive layout.
- Current PDF is exactly two pages, visually inspected; browser-downloaded guide bytes equal the packaged guide. Desktop and mobile interface screenshots inspected.
- Final archive checked for safe paths, CRC and every file hash; executable source/assets/config/model/data/archive matched the separately tested extraction. Numerical services, kernels, trained model, benchmark data and preserved original source archive match v5.1 unchanged.

## Evidence
`docs/V6_INTERFACE_REPORT.md`, `docs/v6_extracted_pytest_results.txt`, `docs/v6_extracted_browser_console.txt`, `docs/v6_extracted_visual_browser_console.txt`, browser result JSON files and fresh-environment logs. Earlier reports are retained as historical validation background, not current main-entry instructions.

## Not executed / limits
No remote account publication, Docker build/run, Windows/macOS execution, calibrated physical microphone or industrial/run-to-failure validation. Virtual microphone testing verifies software recording flow only. Native recording is not continuous live telemetry; sound is not certified SPL/dBA, and RUL is conditional planning rather than guaranteed lifetime. Benchmark classification does not certify severity, localization or safe operation.
