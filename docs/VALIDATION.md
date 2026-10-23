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


## Successful Windows build — 2026-10-23 (supersedes earlier packaging status)

Repository: hamaatahir2005/shexai. Commit: a557a35fba291e64f0ab6a3d1a95980a329788fc.
Runner: Windows Server 2022 x64; Python 3.12.10.
Run: https://github.com/hamaatahir2005/shexai/actions/runs/39982153041

- Pytest: **24 passed, 1 skipped**. The skipped case requires Windows symlink creation privileges; it passes in Linux checks.
- Frozen executable self-test: **status ok**. Verified Qt desktop initialization, SQLite Sorani round trip, real React project files, and optional speech/credential module imports. The temporary workspace cleaned up successfully after explicit SQLite connection closure.
- PyInstaller executable and portable ZIP built successfully.
- Inno Setup installer compiled successfully.
- Download artifact: SheikhHamamomin-Windows-x64, ID 12514112774, 265,606,435 bytes. Includes installer/SheikhHamamomin-Setup.exe, portable ZIP, SHA256, and self-test JSON.
- Outer artifact SHA256: 1d2984d20df4006eae52c1e64309e064fa623b4814c9652b407ed6efe29c4932.

Initial Windows attempts exposed slash-rooted manifest paths and delayed SQLite handle closure. Both were fixed and covered by tests before the successful build. Packaging diagnostics are retained in the workflow.

Still unvalidated: interactive installer execution/uninstall; clean Windows 10 and 11 machines; real microphone/speakers and Sorani speech quality; real API services; physical desktop automation; generated frontend npm build. A successful packaging smoke test is not evidence of those integrations.


## Public download fix — 2026-10-23

Actions artifact links require GitHub sign-in and were reported as 404. Published the existing verified binaries as public Release v0.1.0 through workflow run 39984190511. Verified the source portable ZIP SHA256, packaged self-test status, and installer PE header before publishing. Release API confirms a non-draft release and all five assets uploaded. Installer: 105,796,425 bytes; portable ZIP: 160,885,718 bytes. Public links do not require Actions artifact authentication.

Release: https://github.com/hamaatahir2005/shexai/releases/tag/v0.1.0
