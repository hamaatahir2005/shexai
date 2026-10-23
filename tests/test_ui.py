from hamamomin.ui import Window
from hamamomin.storage import Memory

def test_window_and_offline_chat(qtbot,tmp_path):
    Memory(tmp_path).set('setup',True)
    window=Window(tmp_path)
    qtbot.addWidget(window);window.show()
    assert window.pages.count()==5
    window.entry.setText('hello');window.send()
    qtbot.waitUntil(lambda:not window.busy,timeout=5000)
    assert len(window.memory.history())==2
    assert 'Model is disabled' in window.chat.toPlainText()
    window.navigate(1)
    window.brief.setPlainText('Kurdish portfolio')
    window.guard.confirm=lambda a,d:True
    window.generate()
    qtbot.waitUntil(lambda:not window.busy,timeout=5000)
    assert (window.guard.workspace/'my-kurdish-site/src/main.tsx').exists()
    window.stop();assert window.guard.stopped.is_set()
    window.resume();assert not window.guard.stopped.is_set()
