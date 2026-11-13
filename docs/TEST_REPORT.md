> **Current v6 interface/deployment:** full main application is app.py; streamlit_app.py is a compatibility alias. See V6_INTERFACE_REPORT.md for current69-test/20-browser-check evidence and RaceGuard styling. The report below preserves the preceding numerical/validation cross-check background.

# Streamlit v5.1 — current executed verification
Current cross-checked release. Python3.13.16/Linux x86_64. Current framework:Streamlit1.67.0, Plotly6.5.0.

## Executed results
See **RECHECK_REPORT.md** for newly reproduced defects, fixes and expanded history/export/upload regressions. The current results supersede the earlier46-test/13-workflow build.
- **61 Python tests passed**. This is the new native Streamlit suite, not the previous Gradio/Flask API suite with obsolete endpoint/component expectations. It includes retained numerical monitoring tests plus direct service/model/export tests and native **Streamlit AppTest** sessions.
- Numerical coverage: service-life arithmetic/scenarios/overdue/invalid ordering, exact/noisy linear crossings, approximate conditional ranges, flat/negative/reached thresholds, large-age translation/tiny-slope numerical handling, malformed histories, dB energy averaging, silence/nulls, WAV PCM/channels/clipping and strict finite JSON.
- Direct services: all4 bundled class examples, synthetic/builder processing and nonclassification, real measured upload/manual/geometry, invalid columns/Nyquist, missing metadata serialized as null rather than NaN, RUL budget/demo/user history, WAV/recording/log sources, reference-offset evidence, correct exports and no simulated fallback for absent microphone input.
- AppTest: default startup, actual classification, source/input changes hiding stale current output, invalid synthetic/RUL/sound clearing, conditional RUL demo, sound demo, evidence/PDF screen, and missing recorded-audio input producing a clear error without an unhandled exception. Active imports do not load Gradio or Flask.
- **15 actual Chromium browser workflows passed** with **zero JavaScript page errors** and no Streamlit app exception shown. Includes real classifier/waveform/FFT/features/formulas + JSON download; synthetic success/nonclassification; invalid builder clearing; measured CSV column/domain/classification; RUL scenario bounds/proportional20% meter/error clearing/demo fitted/history plots; generated audio; uploaded reference sine≈−23.01dBFS; overrange numeric preservation with100% clipped meter; external unverified SPL log energy average; native Streamlit **Record→Stop→Analyse→download** using a virtual capture device;390px responsive view.
- Upload/numeric browser helpers wait for native Streamlit rerun/upload completion and commit numeric edits with Enter. Initial exploratory test-selector/timing issues were corrected in the test harness; no failed exploratory run is presented as a passing functional result. Download buttons use on_click='ignore' to avoid unnecessary reruns.
- Microphone testing exercised the **actual st.audio_input component** and server recording analysis, with Chromium's virtual device/WAV fixture. No physical calibrated microphone was available. This confirms software acquisition/processing only, not SPL/dBA accuracy or continuous live streaming.
- Fresh isolated virtual environment installed current requirements and test/PDF tooling; `pip check` found no broken requirements. **No Gradio/Flask runtime dependency or in-process old-web-framework adapter** is needed. Only direct numerical services are used.
- Python source compilation passed. The trained model/evaluation are unchanged. Current PDF **docs/USER_MANUAL.pdf is exactly2 A4 pages**; text/page-count checked and both pages visually inspected. Screenshots are supplementary, not the only evidence.

Raw evidence: pytest_results.txt, browser_results.json, browser_console.txt, clean_install.log, dependency_check.txt. Native screenshots:streamlit_vibration_desktop.png and streamlit_sound_mobile.png. Packaging/extracted-run evidence:PACKAGE_VERIFICATION.md and extracted_* logs.

## Deliberate changes / unsupported claims
- **No continuous live microphone streaming in this release.** Streamlit native audio_input produces completed recordings. The interface, source labels and guides explicitly say this. Former Gradio streaming/encoder/SSE machinery is removed from the active runtime, not relabelled as Streamlit. No fake live reading is substituted.
- Native recordings are uploaded to the server. They are not the historical browser-local AudioWorklet path. Gain/codec/resampling/device preprocessing and actual hardware accuracy are unknown; no certified SPL/dBA/dBC, A/C or IEC time weighting, true peak/exposure compliance claim.
- No real run-to-failure history supplied. Life budgets are entered scenarios; centered-linear threshold extrapolation and fitted-crossing intervals are conditional outputs, not individual life accuracy/survival probabilities. R² is not reliability. Existing CWRU benchmark accuracy is not industrial validation.
- Actual Community Cloud/Hugging Face account publication, Docker build, Windows/macOS execution, cross-browser/device certification and physical microphone/calibrator checks were **not** performed here. Prepared instructions do not count as deployment proof; no public URL is invented.
- Server/session memory and browser downloads are not secure persistent telemetry storage. Permission/HTTPS/host embedding policy can affect recording. Closing the tab/revoking permission may be needed for full hardware release.20MB/300second audio limits are implemented/validated, not a long physical-device endurance qualification.
- All default warning/range/life values are illustrative project examples, not safety/maintenance/occupational standards. Finite unweighted digital arithmetic can be correct without establishing physical measurement accuracy.

## Reproduce
```sh
python -m pip install -r requirements-dev.txt
python -m playwright install --with-deps chromium
python -m pytest -q
python -m streamlit run streamlit_app.py
# Another terminal:
python tests/browser_check.py
```
RACEGUARD_URL selects a nondefault browser test host/port. Test-only fake-device flags are never enabled by normal app launch. Historical full source/reports remain in archive/previous_v4_source.zip, outside the active test/runtime path. These executed checks do not promise zero errors on every OS/browser/host; actual failures should be reported and investigated without fabricating equipment health.
