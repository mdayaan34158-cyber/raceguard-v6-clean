# Start here — Streamlit v6 checked build (not Gradio)

The current FULL main app/interface is **app.py**. Keep **assets/raceguard.css** and **src/presentation.py** for the RaceGuard visual layer. streamlit_app.py is a backwards-compatible alias, not the main implementation. Current guide: **docs/USER_MANUAL.pdf** (2pages). The entire earlier project is preserved only in archive/previous_v4_source.zip; it is not installed or used by the active app. Do not copy its old Gradio/Flask launch files over this root.

## 1. Extract and verify
Download RaceGuard_Streamlit_RaceGuard_UI_v6.zip and fully extract it. Open bearing-streamlit/, containing app.py, README.md, requirements.txt and the .streamlit/ directory. Keep src/, models/, data/ and docs/ in place. Do not run inside the ZIP or flatten subdirectories. DATA_RIGHTS.md explains benchmark redistribution/provenance limitations. Model.joblib is application-owned/trusted; never replace it with an untrusted uploaded pickle/joblib artifact.

## 2. Run on your computer
Install Python3.13, then run RUN_WINDOWS.bat or `sh RUN_MAC_LINUX.sh` from the extracted folder. These create .venv, install requirements.txt and start Streamlit. Internet is needed to install packages. Manual commands are in README.md.

The correct command is **python -m streamlit run app.py**, not plain python app.py, gradio_app.py, launch.py or flask run. Open http://localhost:8501/. Keep terminal open; Ctrl+C stops serving. Localhost is not public hosting. To change port: append `--server.port=8502` (or your chosen port). Native Streamlit serves UI/session/WebSocket traffic; no separate backend/API origin is required.

## 3. Streamlit Community Cloud — recommended hosting
1. Put the extracted project's CONTENTS in a repository accessible to your Community Cloud account. The repository root should contain app.py, requirements.txt and .streamlit/config.toml, not just a ZIP or an extra bearing-streamlit/ wrapper directory. Preserve src/, models/, data/, docs/ and supporting files.
2. Sign in to Streamlit Community Cloud, choose Create app, and select your repository, branch and **app.py** as main/entrypoint file. If suggestions are incomplete, enter the path manually.
3. Advanced settings: choose **Python3.13**, matching the tested pinned environment. No app secrets/GPU are required for included examples. .python-version documents the intended local runtime; selecting the Cloud Python version is still necessary. If a desired runtime is unavailable, use the supplied container route or retest another runtime rather than claiming compatibility.
4. Deploy and read build/runtime logs. Requirements install automatically. Do not install requirements-dev.txt or requirements-docs.txt for normal hosting. There is no Gradio SDK configuration. The current README intentionally does not have old Gradio SDK YAML metadata.
5. Open the actual host-assigned URL. Verify Normal classifier, default RUL budget(800hours illustrative allowance), RUL demo and sound simulation. Then test uploads/recording. Do not invent a public address; this environment did not publish to your account.
6. Review app/repository visibility and DATA_RIGHTS.md before making benchmark excerpts public. Do not upload secrets or private industrial recordings into a public repository. The archive/ prior-source ZIP can be omitted from production if not needed; it is included in the delivered full package for preservation.

Official workflow reference checked: https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/deploy . Platform button labels/options may change; repository, entrypoint, dependency and runtime selection are the essential settings.

## 4. Optional Docker or Hugging Face container route
The root Dockerfile uses Python3.13, installs only requirements.txt, runs as a non-root user and launches native Streamlit on0.0.0.0:8501. A generic container host must expose/proxy8501 and WebSockets, with HTTPS for microphone access. A Docker build was not executed here.

If using Hugging Face Spaces, select **Docker SDK**, not Gradio SDK (the app framework inside remains Streamlit). Add hosting metadata above the supplied README content:
```yaml
---
title: RaceGuard Streamlit
emoji: ⚙️
colorFrom: blue
colorTo: green
sdk: docker
app_port: 8501
---
```
Keep root Dockerfile/requirements/app paths and preserve directories. This is an optional prepared route, not a claim of remote publication. Streamlit Community Cloud does not need this YAML or Dockerfile.

## 5. Inputs / checks on first use
- **Vibration:** benchmark Normal first. For CSV choose the actual signal column, true fs and known RPM; classification requires declared compatible48kHz drive-end acceleration in g. Otherwise signal mode. Pasted input expects numbers, no CSV header. Synthetic numeric builder is always signal-only. No missing-value imputation/resampling/discarding. Optional geometry computes explanatory frequency markers only.
- **RUL:** replace default age/service-life values with justified assumptions. Min/max total lives are paired and bracket nominal. Trend age,indicator history needs≥6 nonnegative finite ordered unique operating ages and higher-is-worse indicator; same asset/regime. A CWRU snapshot is not run-to-failure evidence. R² is fit quality, not life confidence; reported crossing interval is conditional, not individual bearing survival accuracy.
- **Sound:** demo/WAV/microphone recording/log. Microphone uses Record→Stop→Analyse sound; it is not a continuously live meter. WAV max20MB/300s/8channels/10million selected samples, explicit channel0=first; dBFS convention RMS=1at0dBFS. The included amplitude0.1sine is approximately−23.01dBFS RMS. External logs level_db,duration_sec require a single declared convention and positive durations. Defaults are project examples, not safety/exposure limits.
- **Display:** finish numeric edits with Enter/blur and wait for upload completion. Changed inputs hide old results until rerun. Invalid runs clear current outputs/downloads. Historical vibration results are explicitly marked and do not masquerade as the current configuration. Export JSON/CSV/report before ending the session.

## 6. Privacy and microphone limitations
Recordings are uploaded to the Streamlit server; digital level is not calibrated SPL/dBA. Browser gain/encoding/resampling/device preprocessing are not certified. HTTPS/localhost, permission and actual hardware are required. Host iframe/Permissions Policy may block access; open the direct app URL or use WAV. No simulated value is substituted under a microphone label.

Do not record sensitive audio on public/untrusted hosting. Our app processes uploads/downloads in server/session memory rather than writing microphone files into the project. Framework/session buffers/browser downloads are not secure persistent storage or a certified erasure scheme. Use appropriate access/retention controls. Stop before navigation; close tab/revoke site permission if needed for full device release. There is no continuous live streaming or server-side industrial sound acquisition claim.

## 7. Troubleshooting
- Wrong interface: use the current root/Streamlit command; do not unpack the old archived source into it.
- Dependencies fail: use Python3.13 and current requirements.txt; read actual install errors. Do not install former Gradio pins.
- Page blank/disconnected: verify server/logs/port and reverse-proxy WebSocket forwarding. Keep normal CORS/XSRF protections; the supplied config enables them. .streamlit/config.toml binds0.0.0.0 for containers/previews.
- Uploaded file missing: wait for upload finish/preview, keep real extension and size limit, then analyse. Do not change physical sample rates merely to force classification.
- RUL unavailable: inspect slope, fit quality, indicator reference/limit and genuine chronological evidence. Flat/poor histories intentionally withhold numbers.
- Sound unexpected: check source/channel/range/offset and silence/clipping notices. Defaults are unweighted digital units. An offset note is not calibration certification.
- Changes not visible: restart Streamlit and hard-refresh after replacing files. Current errors are shown without a fake healthy diagnosis. Consult docs/TEST_REPORT.md for executed tests versus untested platforms/hardware.

Windows/macOS instructions, remote publication and Docker are prepared guidance, not executed platform claims. The test report records the fresh Linux environment and actual browser/AppTest runs.
