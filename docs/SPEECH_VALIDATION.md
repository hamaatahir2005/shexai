# Kurdish speech validation protocol

Status: **not run with real Kurdish samples**. No Sorani voice quality claim is justified by this source release.

Use consenting native Sorani speakers and recordings without sensitive data. Record the engine/version, microphone, sample rate, accent, environment, language mix, model path/ID, and voice ID. Keep samples local unless the speaker approves a remote service upload.

Test at least these commands, casual conversation, code-switching, and background noise:

1. حەمەومین چۆنی؟
2. حەمەومین VS Code بکەرەوە
3. حەمەومین وێبسایتی فرۆشتنم بۆ دروست بکە
4. ئەم کۆدە ڕوون بکەرەوە
5. Sheikh Hamamomin, open Chrome.
6. افتح المفكرة

Compare reference transcripts with engine transcripts; report word/character error rates and successful intent routing per accent/language rather than claiming universal support. Test wake phrase misses and false activations. The current wake feature requires recording first.

For TTS, ask native speakers to rate intelligibility, pronunciation, naturalness, Kurdish-specific sounds, numbers, and English technical names. Verify mute, interrupt, slow/fast speech, missing voices, missing model, offline errors, denied upload, and emergency stop. If the voice is unsuitable, retain text-only mode. Archive results with explicit consent; do not commit personal recordings or service credentials.
