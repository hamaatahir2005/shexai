"""Smoke-test the packaged desktop on its target machine without user data."""
import json
import os
import tempfile
from pathlib import Path


def probe(report):
    report=Path(report)
    result={'status':'error','checks':[]}
    app=None
    window=None
    try:
        os.environ['QT_QPA_PLATFORM']='offscreen'
        from PySide6.QtWidgets import QApplication
        from .storage import Memory
        from .ui import Window
        import keyring
        import sounddevice
        import faster_whisper
        import pyttsx3
        app=QApplication.instance() or QApplication([])
        with tempfile.TemporaryDirectory(prefix='hamamomin-check-') as root:
            memory=Memory(root);memory.set('setup',True)
            window=Window(root)
            window.show();app.processEvents()
            if window.pages.count()!=5:
                raise RuntimeError('Desktop pages did not initialize.')
            result['checks'].append('Qt desktop initialized')
            memory.add('user','سڵاو')
            if memory.history()[0]['content']!='سڵاو':
                raise RuntimeError('SQLite Unicode round trip failed.')
            result['checks'].append('SQLite Sorani round trip')
            window.guard.confirm=lambda action,detail:True
            window.coding.generate('probe-site','Local build probe')
            if not (window.guard.workspace/'probe-site/src/main.tsx').is_file():
                raise RuntimeError('Project files missing.')
            result['checks'].append('React project files created')
            window.stop();window.close();app.processEvents()
            window=None
        result['checks'].append('Optional voice and credential modules imported; hardware not tested')
        result['status']='ok'
    except Exception as exc:
        import traceback
        result['error']=f'{type(exc).__name__}: {exc}'
        result['traceback']=traceback.format_exc()
    finally:
        if window is not None:
            window.stop();window.close()
        report.parent.mkdir(parents=True,exist_ok=True)
        report.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    return 0 if result['status']=='ok' else 1
