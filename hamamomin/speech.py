"""Optional speech adapters. Sorani quality requires real-sample validation."""
import io
import threading
import numpy as np


class Speech:
    def __init__(self, memory, guard, level=lambda v: None):
        self.memory, self.guard, self.level = memory, guard, level
        self.muted = True
        self.stream = None
        self.frames = []
        self.engine = None
        self.model = None
        self.cancelled = threading.Event()

    def start(self):
        if self.muted:
            raise RuntimeError('Unmute the microphone first.')
        self.guard.check()
        import sounddevice as sd
        self.frames = []
        self.cancelled.clear()
        def callback(data, count, timing, status):
            if not self.cancelled.is_set() and sum(len(f) for f in self.frames) < 16000 * 30:
                self.frames.append(data.copy())
                self.level(float(np.sqrt(np.mean(data ** 2))))
        self.stream = sd.InputStream(samplerate=16000, channels=1, dtype='float32', callback=callback)
        self.stream.start()

    def end(self):
        if self.stream:
            self.stream.stop()
            self.stream.close()
            self.stream = None
        self.level(0)
        if self.cancelled.is_set() or not self.frames:
            return ''
        audio = np.concatenate(self.frames).flatten()
        self.frames = []
        if self.memory.get('stt_mode', 'local') == 'local':
            from faster_whisper import WhisperModel
            model_path = self.memory.get('whisper_path', '')
            if not model_path:
                raise RuntimeError('Set a downloaded faster-whisper model directory in Settings. No automatic model downloads occur.')
            if self.model is None:
                self.model = WhisperModel(model_path, device='cpu', compute_type='int8', local_files_only=True)
            # Auto language detection avoids claiming a dedicated Sorani model.
            segments, info = self.model.transcribe(audio, language=None, vad_filter=True)
            result = ' '.join(s.text for s in segments)
        else:
            import soundfile as sf
            import httpx
            from .security import Secrets
            endpoint = self.memory.get('endpoint', 'https://api.openai.com/v1').rstrip('/')
            from urllib.parse import urlparse
            parsed = urlparse(endpoint)
            if parsed.scheme != 'https' and not (parsed.scheme == 'http' and parsed.hostname in ('localhost', '127.0.0.1', '::1')):
                raise ValueError('Speech endpoint requires HTTPS or loopback HTTP.')
            self.guard.approve('Upload microphone audio', f'Send this recording to {endpoint}/audio/transcriptions')
            buf = io.BytesIO()
            sf.write(buf, audio, 16000, format='WAV')
            response = httpx.post(endpoint + '/audio/transcriptions', headers={'Authorization': 'Bearer ' + Secrets.get()}, files={'file': ('speech.wav', buf.getvalue(), 'audio/wav')}, data={'model': self.memory.get('stt_model', 'whisper-1')}, timeout=90)
            response.raise_for_status()
            result = response.json()['text']
        self.guard.check()
        return '' if self.cancelled.is_set() else result

    def say(self, text):
        mode = self.memory.get('tts', 'text')
        if mode == 'text':
            return 'Text-only mode.'
        self.cancelled.clear()
        if mode == 'system':
            import pyttsx3
            self.engine = pyttsx3.init()
            voice = self.memory.get('voice', '')
            if voice:
                self.engine.setProperty('voice', voice)
            self.engine.setProperty('rate', self.memory.get('speed', 170))
            self.engine.say(text)
            self.engine.runAndWait()
        elif mode == 'external':
            import httpx
            import sounddevice as sd
            import soundfile as sf
            from urllib.parse import urlparse
            from .security import Secrets
            url = self.memory.get('tts_endpoint', '')
            parsed = urlparse(url)
            if parsed.scheme != 'https' and not (parsed.scheme == 'http' and parsed.hostname in ('localhost', '127.0.0.1', '::1')):
                raise ValueError('TTS requires HTTPS or loopback HTTP.')
            self.guard.approve('Send text to TTS service', f'{url}\n{text[:4000]}')
            result = httpx.post(url, json={'input': text, 'voice': self.memory.get('voice', ''), 'model': self.memory.get('tts_model', 'tts-1'), 'response_format': 'wav', 'speed': self.memory.get('speed', 170)/170}, headers={'Authorization': 'Bearer ' + Secrets.get()}, timeout=90)
            result.raise_for_status()
            self.guard.check()
            if not self.cancelled.is_set():
                samples, rate = sf.read(io.BytesIO(result.content))
                sd.play(samples, rate)
                sd.wait()
        return 'Speech finished. Voice availability depends on your installed engine.'

    def stop(self):
        self.cancelled.set()
        if self.stream:
            self.stream.abort()
            self.stream.close()
            self.stream = None
        self.frames = []
        if self.engine:
            self.engine.stop()
        try:
            import sounddevice as sd
            sd.stop()
        except ImportError:
            pass
        self.level(0)


def wake_match(text):
    normalized = text.casefold().replace('ە', 'ە')
    return any(phrase in normalized for phrase in ('sheikh hamamomin', 'حەمەومین', 'شێخ حەمەومین'))
