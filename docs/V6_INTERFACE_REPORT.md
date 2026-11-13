# RaceGuard v6 — native Streamlit interface and app.py deployment

## What is the main application?
**app.py contains the full main interface/application implementation**: imports, page setup, native input controls, rerun/session handling, analysis dispatch, plots, downloads, history, RUL/sound/evidence pages and sidebar/header composition. It is not an empty placeholder or iframe launcher. Numerical algorithms are deliberately separated into src/ for validation/testing rather than duplicated into an enormous UI script.

**streamlit_app.py is a compatibility entry point only**, executing the same app.py. Preferred command: `python -m streamlit run app.py`. Community Cloud main file: **app.py**. RUN scripts, Dockerfile, README, deployment guide and current two-page PDF now use app.py. Upload the entire project, especially assets/raceguard.css, src/, models/, data/ and docs/.

## RaceGuard appearance retained within Streamlit
- Original dark/slate background/panels, mint/cyan accents, amber educational notice and RaceGuard circular logo/CONDITION INTELLIGENCE branding.
- Sidebar workspace navigation with active state, academic project-name eyebrow, Analysis studio / RUL / Sound / Evidence page heroes and separate software-readiness badge.
- Evidence-driven KPI cards for result, actual RMS, completed windows and vote agreement; empty state is explicitly Not assessed, never fabricated equipment health.
- Bearing component illustration with neutral/no-assessment state before a run; benchmark-class mapping only when classification is performed. Synthetic/signal-only data never highlight an inferred fault. Labels explicitly deny measured spatial localization, scale accuracy, severity or safety inference.
- Styled native source controls, status metrics, real waveform/FFT and RUL/sound charts, history, formulas and downloads. Native controls and rerun/recording behavior remain Streamlit; this is **not claimed pixel-identical to the old HTML/JavaScript dashboard**.
- Mobile CSS adapts hero/KPI grid and native layout without document horizontal overflow. No external CSS/font/image CDN or a separate dashboard iframe is required.

## Browser rendering issue found and fixed
Streamlit's HTML sanitizer removed inline SVG markup from the initial visual implementation. Rather than ship a blank bearing/logo, the logo is now CSS and the SVG bearing is embedded as a local base64 image with the proper SVG namespace. A dedicated real-browser test verifies the bearing image has a nonzero natural width (actually decoded/displayed), not merely that markup exists. Separate current/history identifiers and chart keys avoid duplicate-element conflicts.

## Executed current tests
- **69 Python tests passed**: all61 previous fixed Streamlit/numerical regressions, plus8 main-entry/visual tests. Both canonical app.py and compatibility streamlit_app.py produce the same actual model result. Canonical app.py's Vibration/RUL/Sound/Evidence pages were exercised through native Streamlit AppTest. Visual helpers escape data, preserve unavailable states, distinguish synthetic from class mapping and bundle offline styling.
- **15 functional Chromium workflows passed** against the **app.py** server: classifier/FFT/features/formulas/downloads, current+history charts, synthetic/nonclassification, invalid-input clearing, measured upload, RUL budget/scenario/range/history, sound simulation/reference WAV/logs/overrange, virtual-microphone Record→Stop→Analyse→export, PDF download and mobile view.
- **5 additional visual/browser checks passed**: actual RaceGuard branding/colors/KPIs/hero, loaded neutral bearing image before assessment, real-data-driven Normal KPI/illustration/plots, simultaneous current/history image/chart views, responsive390px two-column KPI grid/no horizontal document overflow.
- Both browser suites reported **zero JavaScript page errors** and no Streamlit exception shown. Screenshots raceguard_v6_desktop.png and raceguard_v6_mobile.png were generated from the real running app; they are supplementary, not the only evidence.
- Fresh isolated environment install/pip check/source compilation passed. Gradio/Flask are not installed or used by the active runtime. Trained model, numerical services and data artifacts remain unchanged by the interface update.
- **docs/USER_MANUAL.pdf remains exactly2 A4 pages**, now instructing app.py deployment and keeping assets/. The UI-downloaded copy matches the packaged guide.
- Separately extracted ZIP testing and runtime/source integrity are recorded in PACKAGE_VERIFICATION.md and v6_extracted_* evidence.

Current raw evidence: v6_pytest_results.txt, v6_browser_console.txt, browser_results.json, v6_visual_browser_console.txt, v6_visual_browser_results.json, v6_clean_install.log and v6_dependency_check.txt. Older reports/logs refer to previous releases and are retained history.

## Limits preserved
Streamlit native microphone is completed recording analysis, **not continuous live streaming**. Audio goes to the server; physical microphone/calibration accuracy was not established (virtual-device tests only). dBFS is not certified SPL/dBA. RUL remains declared assumptions/conditional fitted-trend planning, not a fault-class shortcut, calibrated survival probability or guaranteed lifetime. Default alerts are project examples, not safety standards. Actual Community Cloud account publication, Docker build, Windows/macOS and other-device certification were not performed. Visual similarity does not change the model's narrow benchmark validation scope or make the system safety-critical software.
