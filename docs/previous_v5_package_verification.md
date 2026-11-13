# Streamlit v5 — full package verification
07 November2026.

1. Built a complete native Streamlit project, not a patch/wrapper. Active code uses Streamlit and direct numerical services. Runtime requirements do not include Gradio/Flask. Full previous delivered source is preserved byte-for-byte as archive/previous_v4_source.zip, not used by the active app.
2. Created a fresh isolated Python3.13.16 environment and installed current pinned runtime/development/PDF dependencies. pip check: no broken requirements. Gradio and Flask are not installed in this environment; active tests and server work without them.
3. Built ZIP with bearing-streamlit/ root and SHA256SUMS.txt. Extracted to a separate folder; ZIP CRC and every per-file SHA256 matched. Runtime source, trained model, data/manifest, samples, .streamlit configuration, requirements, launch scripts, Dockerfile, tests, instructions and current2-page PDF were present.
4. Ran the new suite **from the extracted root** in the fresh environment: **46 passed**. See docs/extracted_pytest.txt. Module paths in docs/extracted_modules.txt confirm imported services/model code resolve to the extracted copy, with no Gradio/Flask installed.
5. Started extracted `python -m streamlit run streamlit_app.py --server.port=8502`, binding0.0.0.0. Ran all **13 native Chromium workflows** against it: passed, including actual virtual-microphone Record→Stop→Analyse→download. See docs/extracted_browser.txt. This is completed-clip analysis, not continuous live streaming or calibrated physical hardware validation.
6. Added these verification records and rebuilt the final ZIP. Runtime code/config/dependencies match the extracted tested copy; only verification documentation/logs were added afterward. Final ZIP was checked again for CRC, required/safe paths, all per-file hashes, preserved previous-source archive, unchanged trained-model bytes and exactly2 pages in docs/USER_MANUAL.pdf.

Current source/guide/deployment are all Streamlit. Older instructions inside the archive are historical only. Docker/cloud/Windows/macOS execution and physical acoustic/run-to-failure accuracy remain unvalidated; prepared configs/instructions are not claims of remote publication or universal error-free operation. See docs/TEST_REPORT.md for complete scope.

On systems with sha256sum, verify extracted files from the project root with `sha256sum -c SHA256SUMS.txt`. The manifest includes all packaged regular files except itself; environments, caches, bytecode and secrets are excluded.
