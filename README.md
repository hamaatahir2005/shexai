# SHEIKH HAMAMOMIN AI — شێخ حەمەومین

A Python 3.12 Windows desktop assistant with a PySide6 interface, local SQLite memory, explicit action permissions, Sorani-first prompting, and a real project generator. This is an implemented MVP with a Windows x64 executable and installer built and smoke-tested on GitHub Actions (Windows Server 2022). It is not a production-certified release.

## Download the Windows application

[Download Windows installer (106 MB)](https://github.com/hamaatahir2005/shexai/releases/download/v0.1.0/SheikhHamamomin-Setup.exe) — public download, no GitHub sign-in needed. Open the downloaded EXE and follow the setup wizard. Python is not required.

[Portable ZIP (161 MB)](https://github.com/hamaatahir2005/shexai/releases/download/v0.1.0/SheikhHamamomin-Windows-x64.zip) — fully extract it and run the EXE inside its folder. [All release files and checksums](https://github.com/hamaatahir2005/shexai/releases/tag/v0.1.0).

[Successful build and test report](https://github.com/hamaatahir2005/shexai/actions/runs/39982153041): 24 tests passed, one symlink test skipped; the frozen EXE passed Qt startup, SQLite Sorani storage, real React file generation, and optional module imports. Installer compilation succeeded; interactive installation, physical audio devices, Kurdish speech quality, and clean Windows 10/11 user machines still require validation. API/model configuration is required for AI chat.

## Run from source on Windows 10 / 11

Install Python 3.12 (64-bit), then open PowerShell in this directory:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/install.ps1
.\.venv\Scripts\hamamomin.exe
```

For just the desktop/text features, install the base package instead:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e .
.\.venv\Scripts\hamamomin.exe
```

A first-run guide explains configuration. All runtime files initialize in `%LOCALAPPDATA%\SheikhHamamomin`, including `memory.sqlite3` and `projects/`. The project directory contains the database implementation; the user's database is created at first run rather than shipping personal data.

## Configure models

Settings → enable model → choose base URL and model. OpenAI-compatible services use an endpoint such as `https://api.openai.com/v1`. Ollama uses `http://127.0.0.1:11434/v1` with an already downloaded model such as `qwen2.5-coder:7b`. Model availability and Sorani proficiency vary. A remote model requires internet and usually an API key; Ollama needs installation and a model download but can run offline afterward.

Enter the key in Settings; it is stored through `keyring` using the OS credential backend (Windows Credential Manager). No plaintext fallback is used. An optional `HAMAMOMIN_API_KEY` environment variable is supported; `.env.example` documents it. Protect any `.env` yourself. A blank Settings key field retains the existing key; a separate button removes the stored key. The environment key, if configured, remains available until removed from the environment.

Each model call asks approval. Chat sends the last 24 saved messages, the current message, and approved preferences. Review/edit/export/delete context in Memory. Studio sends its brief; Explain sends the selected source file. The application never converts model replies into shell commands.

## Desktop and coding

Enable desktop automation in Settings. Each launch, URL, screenshot, or media action also requires confirmation. Supported apps: native VS Code, Chrome in standard locations, Notepad, and Explorer. VS Code discovery checks PATH and common install directories. Desktop operations require Windows for meaningful validation. Screenshots stay local.

Examples:

- `حەمەومین چۆنی؟`
- `حەمەومین VS Code بکەرەوە`
- `Open Chrome`
- `حەمەومین وێبسایتی فرۆشتنم بۆ دروست بکە`
- `Build a website for my portfolio`

Website requests open Studio and ask about audience, pages, languages, and data requirements. Fill the brief, create a plan, choose a lowercase project slug, then Generate. The offline generator creates a responsive React/TypeScript/Vite/Tailwind frontend with real source files and README. It does **not** implement checkout or a backend. Other stacks and custom backends require AI generation, whose output needs review and may need fixes. No generated project is claimed tested merely because generation succeeds.

Studio supports read/edit, AI code explanation, Python syntax checking, and approved commands: dependency install, build, test, preview, git init/status. Dependencies require Node.js 20+ and internet; `npm install` disables lifecycle scripts. Build/test/preview execute project code and explicitly warn before execution. The local starter has a build command but no application test suite; add meaningful tests before running its test control. Preview binds to loopback and stops after ten minutes. Open `http://127.0.0.1:5173` through Tools after Vite reports readiness. VS Code and Git must be installed separately. No automatic software installation occurs.

## Voice: optional and unvalidated for Sorani

Install `.[voice]`. Unmute the microphone, Record, then Finish recording. Recordings are capped at 30 seconds. Review the transcript before pressing Send. Whisper auto-detects language; no dedicated Sorani support or accuracy guarantee is claimed.

- Local recognition: download a faster-whisper/CTranslate2 model separately, then set its directory in Settings. This application does not automatically download models.
- Remote recognition: choose `remote`; recordings go to the configured model base URL `/audio/transcriptions` only after confirmation. Requires a Whisper-compatible service and usually a key/internet.
- Speech output: default is text-only. `system` uses pyttsx3 and installed Windows voices, which may not include Sorani. Set a valid installed voice ID.
- External speech: set a full OpenAI-compatible TTS URL ending in `/audio/speech`, a voice ID, and model. Service must return WAV and support the selected language. Sending text requires confirmation. The same credential is used for model/STT/TTS services; configure only trusted destinations.
- Read last speaks the last assistant response. Interrupt stops playback/recording; cancellation of underlying model computation may wait for its return. Emergency stop discards late results and terminates managed command descendants. Already sent network data cannot be recalled.
- Wake mode checks the phrases `Sheikh Hamamomin` and `حەمەومین` in recorded transcripts. It is **not continuous wake-word detection**.

Real Kurdish samples were not available in this environment. See [speech validation](docs/SPEECH_VALIDATION.md) before claiming Kurdish voice compatibility.

## UI and local memory

Dark cyan desktop interface, animated orb, microphone waveform, CPU/RAM readings, conversation area, active-task status, Studio output, settings, and optional RTL layout. Voice dependencies load only when needed. Memory provides message editing, preference editing, JSON export, and deletion of history/preferences/audit logs. API keys are excluded from SQLite exports. Project files persist after clearing memory.

## Security boundaries

Files and searches are restricted to the assistant's project workspace with resolved-path checks, symlink escape prevention, and Windows device-name restrictions. Generated manifests are size/count bounded, validated before writes, staged, and never overwrite an existing project. Edits require confirmation. There is no delete tool, arbitrary shell, global folder search, unrestricted GUI clicking, or autonomous model tool execution. `pyautogui` is limited to approved screenshot/media operations. No window management is implemented yet. Playwright is an optional dependency reserved for future browser workflows; there is no browser automation agent yet.

Treat AI-generated code as untrusted. Named npm commands still execute scripts and dependencies and are not a sandbox. Review source before approving. SQLite is local but not encrypted; use Windows disk encryption and a protected account. Emergency stop cannot roll back completed edits or external side effects. This MVP is not hardened against an adversarial local process modifying files concurrently.

## Tests and validation

```powershell
.\.venv\Scripts\python.exe -m pytest -q
# Headless Qt, where applicable:
$env:QT_QPA_PLATFORM='offscreen'
.\.venv\Scripts\python.exe -m pytest -q
```

Dependency-light checks:

```sh
PYTHONPATH=. python tests/smoke_stdlib.py
```

See [validation status](docs/VALIDATION.md) for what was actually run. Mocked API/process checks are not live integration evidence.

## Windows packaging

```powershell
powershell -ExecutionPolicy Bypass -File scripts/build.ps1
```

Build on Windows; PyInstaller does not cross-compile Windows executables from Linux. The script generates a custom icon and a windowed `dist/SheikhHamamomin/SheikhHamamomin.exe`. Install Inno Setup 6 separately and compile `scripts/installer.iss` to create the per-user installer with Start Menu shortcut and optional desktop shortcut. Speech dependencies can substantially increase package size. Test the executable on a clean Windows 10 and Windows 11 machine before distribution; signing and automatic updates are not implemented.

Optional read-only local service:

```sh
uvicorn hamamomin.service:app --host 127.0.0.1 --port 8765
```

Only `/health` is exposed; no remote desktop tools or memory endpoints.

## Modules

`ui.py`: desktop and approval dialogs; `llm.py`: persona and compatible model client; `storage.py`: SQLite; `security.py`: paths/permissions/credentials; `tools.py`: desktop and allowlisted process control; `coding.py`: project generation and edits; `speech.py`: optional STT/TTS; `intents.py`: conservative local routing; `service.py`: optional health service.

Future work: continuously listening wake detector, verified Sorani speech models, broader window/browser control, richer project planning and automated repair, encrypted memory, signed Windows releases, and production security review.

## One-click Windows build (updated)

See [ڕێنمایی کوردی](START-HERE-KU.md). On Windows x64 with Python 3.12 installed, double-click `BUILD-WINDOWS.cmd` and approve downloading build dependencies. It creates a local virtual environment, installs dependencies, runs tests, freezes the app, runs the packaged `--self-test`, and creates `dist/SheikhHamamomin-Windows-x64.zip`. Extract the entire ZIP before launching the EXE; do not copy the EXE alone.

For a setup installer, install Inno Setup 6 and run `scripts/build.ps1 -Installer`. The manual GitHub Actions workflow `.github/workflows/windows-build.yml` performs the Windows build and uploads the portable ZIP, installer, SHA256, and self-test report. The workflow successfully built the Windows package on 2026-10-23. Use the download link above for binaries; source ZIPs do not contain the prebuilt EXE.
