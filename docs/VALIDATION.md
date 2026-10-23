# Validation record

Environment: Python 3.12.14, Linux, 2026-10-22.

Executed successfully:

- `python -m compileall -q hamamomin`: syntax compilation.
- `PYTHONPATH=. python tests/smoke_stdlib.py`: **14 tests passed**. Covers SQLite persistence/edit/export/delete, path traversal and device names, symlink escape, permission denial, emergency gate, real React file creation/no overwrite, unsafe AI manifests, approved edits/Python syntax, command allowlist, mocked subprocess execution, multilingual local intents, denied and mocked model calls, and transcript wake matching.
- `python scripts/make_icon.py`: ICO/PNG artifacts generated.
- A real offline React starter is included in `examples/kurdish-portfolio/`. Its dependencies were not installed and its build was not run here.

Not executed:

- Pytest suite and Qt GUI smoke test: pytest and PySide6 are unavailable. Dependency installation encountered blocked network access; an additional-permissions retry was canceled. No screenshot/UI runtime claim is made.
- Live LLM, remote STT/TTS: no credentials or configured services.
- Local Whisper transcription: no downloaded model or real recordings.
- Native Kurdish speech evaluation: no samples/native-speaker validation.
- Windows app launches, screenshots, media key, credential-store backend, packaging and installer: this environment is Linux.
- Generated frontend npm install/build and Playwright/browser tests.

Before release: install dependencies on Windows, run pytest, exercise all permission/stop paths, build the frontend starter, validate real speech, build the executable and installer, and test them on clean Windows 10 and 11 machines. This source release is an MVP with explicit limitations, not completion of every feature in the original vision.

2026-10-23 packaging update:

- Added one-click Windows builder with checked native exit codes, full dependency setup, tests, PyInstaller build, packaged self-test, ZIP and SHA256 output, and optional Inno Setup invocation.
- Added manual Windows GitHub Actions workflow, Kurdish instructions, and packaged Qt/SQLite/project-generation probe.
- Re-ran all 14 dependency-light checks successfully and syntax-compiled Python modules.
- Windows build, PowerShell execution, frozen-app probe and workflow remain unexecuted: no Windows runtime or authenticated build runner is available in this session. No Windows executable was generated.
