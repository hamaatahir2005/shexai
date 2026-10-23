import html
import json
import math
import threading
from pathlib import Path
from PySide6.QtCore import Qt, QThread, Signal, QTimer, QRectF
from PySide6.QtGui import QColor, QPainter, QPen, QRadialGradient, QFont, QIcon
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QLabel, QPushButton, QStackedWidget, QTextBrowser, QLineEdit, QPlainTextEdit, QFormLayout, QCheckBox, QComboBox, QSpinBox, QMessageBox, QFileDialog, QDialog, QDialogButtonBox, QInputDialog, QFrame, QSplitter, QScrollArea)
from .storage import Memory
from .security import Guard, Secrets
from .tools import Tools
from .llm import LLM
from .coding import CodingAgent

STYLE = '''
QWidget {background:#080f1d; color:#deedf7; font-family:'Segoe UI',Tahoma; font-size:13px;}
QMainWindow {background:#080f1d;}
QLabel#brand {font-size:19px;font-weight:700;letter-spacing:2px;color:#7ee8ff;}
QLabel#title {font-size:28px;font-weight:700;}
QLabel#muted {color:#7d92ab;}
QFrame#card {background:#101d30;border:1px solid #21344c;border-radius:16px;}
QPushButton {background:#12263b;border:1px solid #28435d;border-radius:9px;padding:11px 17px;text-align:left;}
QPushButton:hover {background:#1c3b52;border-color:#54dfff;}
QPushButton:checked {background:#153c51;color:#78eaff;border-color:#3cbbd7;}
QPushButton#primary {background:#58dcf4;color:#051321;font-weight:700;border:0;}
QPushButton#danger {color:#ff9baa;border-color:#73364c;background:#301c30;}
QLineEdit,QPlainTextEdit,QTextBrowser,QComboBox,QSpinBox {background:#0d1829;border:1px solid #253b54;border-radius:8px;padding:10px;selection-background-color:#215c75;}
QTextBrowser {border:0;}
QScrollArea {border:0;}
QCheckBox {spacing:10px;padding:5px;}
QComboBox QAbstractItemView {background:#13253a;}
'''


class Job(QThread):
    result = Signal(str)
    error = Signal(str)
    def __init__(self, fn):
        super().__init__()
        self.fn = fn
    def run(self):
        try:
            self.result.emit(str(self.fn()))
        except Exception as exc:
            # Never echo HTTP request headers or credentials.
            self.error.emit(f'{type(exc).__name__}: {str(exc)[:700]}')


class Bridge(QWidget):
    permission = Signal(object)
    output = Signal(str)
    level = Signal(float)


class Orb(QWidget):
    def __init__(self):
        super().__init__()
        self.setMinimumHeight(265)
        self.phase, self.level, self.active = 0, 0, False
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.tick)
        self.timer.start(40)
    def tick(self):
        self.phase += .025
        self.update()
    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        x,y = self.width()/2,self.height()/2-12
        r = min(self.width()/3, 89)
        g = QRadialGradient(x,y,r*1.5)
        g.setColorAt(0,QColor(34,160,214,140));g.setColorAt(.65,QColor(25,109,163,75));g.setColorAt(1,QColor(8,15,29,0))
        p.setPen(Qt.PenStyle.NoPen);p.setBrush(g);p.drawEllipse(QRectF(x-r*1.5,y-r*1.5,r*3,r*3))
        p.setBrush(Qt.BrushStyle.NoBrush)
        for i in range(5):
            rr = r*(.54+i*.14)+math.sin(self.phase*2+i)*2
            p.setPen(QPen(QColor(84,218,255,210-i*25),1.5))
            p.drawArc(QRectF(x-rr,y-rr,rr*2,rr*2),int((self.phase*(30 if i%2 else -30)+i*60)*16),int((180+i*23)*16))
        p.setPen(QColor('#a9f4ff'));p.setFont(QFont('Segoe UI',23,QFont.Weight.Light));p.drawText(QRectF(x-60,y-25,120,50),Qt.AlignmentFlag.AlignCenter,'حەمەومین')
        p.setPen(QPen(QColor('#53d7f3'),2))
        for i in range(43):
            amp = 2 + (self.level*300 if self.active else 3)*(1+math.sin(i*.9+self.phase*4))
            xx = x+(i-21)*5
            p.drawLine(int(xx),int(y+r+25-amp),int(xx),int(y+r+25+amp))


def button(text, fn=None, primary=False):
    b = QPushButton(text)
    if primary:b.setObjectName('primary')
    if fn:b.clicked.connect(fn)
    return b


def heading(layout, title, detail=''):
    l=QLabel(title);l.setObjectName('title');layout.addWidget(l)
    if detail:
        l=QLabel(detail);l.setObjectName('muted');l.setWordWrap(True);layout.addWidget(l)


class Window(QMainWindow):
    def __init__(self, root=None):
        super().__init__()
        self.setWindowTitle('SHEIKH HAMAMOMIN AI • شێخ حەمەومین')
        self.resize(1320,850);self.setMinimumSize(960,680)
        self.memory=Memory(root); self.jobs=[];self.pending=[];self.speech=None;self.recording=False;self.busy=False
        self.bridge=Bridge();self.bridge.permission.connect(self.permission);self.bridge.output.connect(self.log);self.bridge.level.connect(self.audio_level)
        self.guard=Guard(self.memory.root/'projects',self.memory,self.confirm)
        self.tools=Tools(self.guard,self.bridge.output.emit);self.llm=LLM(self.memory,self.guard);self.coding=CodingAgent(self.guard,self.llm)
        self.setStyleSheet(STYLE)
        host=QWidget();self.setCentralWidget(host);outer=QHBoxLayout(host);outer.setContentsMargins(20,20,20,20);outer.setSpacing(22)
        sidebar=QVBoxLayout();sidebar.setSpacing(12);outer.addLayout(sidebar,0)
        brand=QLabel('◈  HAMAMOMIN');brand.setObjectName('brand');sidebar.addWidget(brand)
        sub=QLabel('PERSONAL INTELLIGENCE\nشێخ حەمەومین');sub.setObjectName('muted');sidebar.addWidget(sub);sidebar.addSpacing(30)
        self.pages=QStackedWidget();self.nav=[]
        for i,text in enumerate(['◉  Command center','⌘  Project studio','◇  Desktop tools','▤  Memory','⚙  Settings']):
            b=button(text,lambda checked=False,n=i:self.navigate(n));b.setCheckable(True);sidebar.addWidget(b);self.nav.append(b)
        sidebar.addStretch();self.mic=button('Microphone muted',self.toggle_mute);sidebar.addWidget(self.mic)
        stop=button('■  EMERGENCY STOP',self.stop);stop.setObjectName('danger');sidebar.addWidget(stop)
        sidebar.addWidget(button('Resume assistant',self.resume));sidebar.addWidget(QLabel('LOCAL MEMORY • APPROVAL REQUIRED'))
        outer.addWidget(self.pages,1)
        self.make_chat();self.make_studio();self.make_tools();self.make_memory();self.make_settings();self.navigate(0)
        self.timer=QTimer(self);self.timer.timeout.connect(self.metrics);self.timer.start(1500);self.metrics()
        for row in self.memory.history():self.append_chat(row['role'],row['content'])
        if not self.memory.get('setup',False):QTimer.singleShot(200,self.wizard)

    def page(self):
        w=QWidget();v=QVBoxLayout(w);v.setContentsMargins(0,0,0,0);v.setSpacing(15);self.pages.addWidget(w);return v
    def navigate(self,n):
        self.pages.setCurrentIndex(n)
        for i,b in enumerate(self.nav):b.setChecked(i==n)
        if n==3:self.refresh_memory()
    def confirm(self,action,detail):
        request={'action':action,'detail':detail,'done':threading.Event(),'allowed':False}
        self.bridge.permission.emit(request)
        while not request['done'].wait(.1):
            if self.guard.stopped.is_set():return False
        return request['allowed']
    def permission(self,r):
        if self.guard.stopped.is_set():r['done'].set();return
        self.pending.append(r)
        dialog=QMessageBox(self);dialog.setWindowTitle('Permission required');dialog.setText(r['action']);dialog.setInformativeText('Review the details before allowing this action.');dialog.setDetailedText(r['detail']);dialog.setStandardButtons(QMessageBox.StandardButton.Yes|QMessageBox.StandardButton.No);dialog.setDefaultButton(QMessageBox.StandardButton.No)
        # Nonblocking dialog keeps emergency stop accessible in the main window.
        dialog.setWindowModality(Qt.WindowModality.NonModal)
        def finish(result):
            r['allowed']=result==QMessageBox.StandardButton.Yes and not self.guard.stopped.is_set();r['done'].set()
            if r in self.pending:self.pending.remove(r)
            dialog.deleteLater()
        dialog.finished.connect(finish);dialog.show();r['dialog']=dialog
    def run(self,fn,callback=None):
        if self.busy:
            self.log('Another task is active. Stop it or wait for completion.');return
        if self.guard.stopped.is_set():self.log('Emergency stop active. Press Resume assistant.');return
        self.busy=True;self.task.setText('● Working • permission may be required');self.orb.active=True
        job=Job(fn);self.jobs.append(job)
        job.result.connect(callback or self.log);job.error.connect(self.log)
        def done():
            self.busy=False;self.orb.active=False;self.task.setText('● Ready • local workspace protected')
            self.jobs.remove(job);job.deleteLater()
        job.finished.connect(done);job.start()
    def log(self,text):
        self.output.appendPlainText(text);self.task.setToolTip(text[-1000:])
    def append_chat(self,role,text):
        color='#64e3fa' if role=='assistant' else '#c3a9ff'
        self.chat.append(f'<p style="color:{color}"><b>{html.escape(role.upper())}</b></p><p dir="auto">{html.escape(text).replace(chr(10),"<br>")}</p>')
    def make_chat(self):
        v=self.page();heading(v,'Your intelligence. Your command.','SHEIKH HAMAMOMIN AI  /  شێخ حەمەومین  •  Sorani · Arabic · English')
        self.status=QLabel();self.status.setObjectName('muted');v.addWidget(self.status)
        self.orb=Orb();v.addWidget(self.orb)
        self.task=QLabel('● Ready • local workspace protected');self.task.setAlignment(Qt.AlignmentFlag.AlignCenter);v.addWidget(self.task)
        self.chat=QTextBrowser();self.chat.setOpenExternalLinks(False);v.addWidget(self.chat,1)
        self.entry=QLineEdit();self.entry.setPlaceholderText('حەمەومین، چۆنیت؟  /  Ask anything…');self.entry.returnPressed.connect(self.send)
        row=QHBoxLayout();row.addWidget(self.entry,1);row.addWidget(button('Send ↗',self.send,True));self.record=button('● Record',self.record_voice);row.addWidget(self.record);row.addWidget(button('Read last',self.speak_last));row.addWidget(button('Interrupt',self.interrupt));v.addLayout(row)
    def send(self):
        text=self.entry.text().strip()
        if not text or self.busy:return
        self.entry.clear();self.append_chat('user',text)
        from .intents import intent
        action,value=intent(text)
        if action=='launch':
            self.memory.add('user',text)
            def launched(result):
                self.memory.add('assistant',result);self.append_chat('assistant',result)
            self.run(lambda:self.tools.launch(value),launched);return
        if action=='studio':
            self.memory.add('user',text);self.brief.setPlainText(value);self.navigate(1)
            answer='بەسەرچاو گەورەم! پڕۆژەکە بۆ کێیە؟ چ پەڕە و زمانێکت دەوێت؟ پێویستی بە هەژمار، پارەدان یان داتابەیس هەیە؟\nComplete the Studio brief, review the plan, then generate files.'
            self.memory.add('assistant',answer);self.append_chat('assistant',answer);return
        def task():
            result=self.llm.chat(text)
            self.memory.add('user',text);self.memory.add('assistant',result)
            return result
        self.run(task,lambda result:self.append_chat('assistant',result))
    def make_studio(self):
        v=self.page();heading(v,'Project studio','Real files. Reviewable changes. Isolated workspaces.');form=QFormLayout();v.addLayout(form)
        self.project=QLineEdit('my-kurdish-site');form.addRow('Project slug',self.project)
        self.stack=QComboBox();self.stack.addItems(['React + TypeScript','Next.js','HTML + CSS + JavaScript','Node.js API','Python FastAPI']);form.addRow('Stack',self.stack)
        self.brief=QPlainTextEdit();self.brief.setPlaceholderText('Who is it for? Which pages, language, branding, and features? Does it need accounts, checkout, or persistent data?');self.brief.setMaximumHeight(130);v.addWidget(self.brief)
        self.use_ai=QCheckBox('Generate with configured AI model (sends brief for approval)');v.addWidget(self.use_ai)
        row=QHBoxLayout();row.addWidget(button('Create plan',self.plan));row.addWidget(button('Generate files',self.generate,True));row.addWidget(button('Open in VS Code',lambda:self.run(lambda:self.tools.launch('vscode',self.project.text()))));v.addLayout(row)
        row=QHBoxLayout()
        for name in ('install','build','test','preview','git-init','git-status'):
            row.addWidget(button(name,lambda checked=False,n=name:self.run(lambda:self.tools.command(n,self.project.text()))))
        v.addLayout(row)
        row=QHBoxLayout();self.file=QLineEdit();self.file.setPlaceholderText('my-kurdish-site/src/main.tsx');row.addWidget(self.file,1)
        row.addWidget(button('Read',self.read_file));row.addWidget(button('Explain',lambda:self.run(lambda:self.coding.explain(self.file.text()))));row.addWidget(button('Python syntax',lambda:self.run(lambda:self.coding.lint_python(self.file.text()))));row.addWidget(button('Save edit',lambda:self.run(lambda:self.coding.edit(self.file.text(),self.editor.toPlainText()))));v.addLayout(row)
        self.editor=QPlainTextEdit();self.editor.setPlaceholderText('Read a source file here, edit it, then approve Save edit.');v.addWidget(self.editor,1)
        self.output=QPlainTextEdit();self.output.setReadOnly(True);self.output.setMaximumBlockCount(2000);self.output.setPlaceholderText('Plans, file results and command output appear here.');v.addWidget(self.output,1)
    def plan(self):self.log(self.coding.plan(self.brief.toPlainText(),self.stack.currentText()))
    def generate(self):
        brief=self.brief.toPlainText().strip()
        if not brief:self.log('Describe the audience, pages, language and required features first.');return
        if not self.use_ai.isChecked() and self.stack.currentIndex()!=0:self.log('The offline starter supports React + TypeScript. Enable a model for other stacks.');return
        if self.use_ai.isChecked() and not self.memory.get('model_enabled',False):self.log('Enable your model in Settings first.');return
        name=self.project.text();ai=self.use_ai.isChecked();stack=self.stack.currentText()
        self.run(lambda:self.coding.generate(name,brief,ai,stack))
    def read_file(self):self.run(lambda:self.coding.read(self.file.text()),self.editor.setPlainText)
    def make_tools(self):
        v=self.page();heading(v,'Desktop tools','Automation is disabled by default. Each action requires approval. Searches stay inside the assistant workspace.')
        for name,label in [('vscode','Open Visual Studio Code'),('chrome','Open Chrome'),('explorer','Open project workspace'),('notepad','Open Notepad')]:v.addWidget(button(label,lambda checked=False,n=name:self.run(lambda:self.tools.launch(n))))
        row=QHBoxLayout();self.url=QLineEdit('http://127.0.0.1:5173');row.addWidget(self.url);row.addWidget(button('Open URL',lambda:self.run(lambda:self.tools.website(self.url.text()))));v.addLayout(row)
        row=QHBoxLayout();self.query=QLineEdit();self.query.setPlaceholderText('Filename fragment');row.addWidget(self.query);row.addWidget(button('Search workspace',lambda:self.run(lambda:self.tools.search(self.query.text()))));v.addLayout(row)
        v.addWidget(button('Screenshot → local workspace',lambda:self.run(self.tools.screenshot)));v.addWidget(button('Media play / pause',lambda:self.run(self.tools.media)))
        v.addWidget(QLabel('Tool results appear in Project studio output. No arbitrary shell commands are accepted.'));v.addStretch()
    def make_memory(self):
        v=self.page();heading(v,'Your memory, under your control','History, approved preferences, project/task audit and settings are stored locally in SQLite.')
        self.memory_view=QPlainTextEdit();self.memory_view.setReadOnly(True);v.addWidget(self.memory_view,1)
        row=QHBoxLayout();row.addWidget(button('Refresh',self.refresh_memory));row.addWidget(button('Add / edit preference',self.add_preference));row.addWidget(button('Edit message',self.edit_message));row.addWidget(button('Export JSON',self.export_memory));row.addWidget(button('Delete stored history',self.delete_memory));v.addLayout(row)
    def refresh_memory(self):self.memory_view.setPlainText(json.dumps(self.memory.export(),indent=2,ensure_ascii=False))
    def add_preference(self):
        key,ok=QInputDialog.getText(self,'Approved preference','Preference name')
        if not ok or not key:return
        value,ok=QInputDialog.getText(self,'Approved preference','Value (sent with future model conversations if approved)',text=self.memory.preferences().get(key,''))
        if ok:self.memory.preference(key,value);self.refresh_memory()
    def edit_message(self):
        mid,ok=QInputDialog.getInt(self,'Edit history','Message ID',1,1)
        if not ok:return
        content,ok=QInputDialog.getMultiLineText(self,'Edit history','Replacement content')
        if ok:self.memory.edit_message(mid,content);self.refresh_memory()
    def export_memory(self):
        path,_=QFileDialog.getSaveFileName(self,'Export memory','','JSON (*.json)')
        if path:Path(path).write_text(json.dumps(self.memory.export(),ensure_ascii=False,indent=2),encoding='utf-8')
    def delete_memory(self):
        if QMessageBox.question(self,'Delete memory','Permanently delete conversations, preferences, and task/project logs? Settings and project files are preserved.',QMessageBox.StandardButton.Yes|QMessageBox.StandardButton.No,QMessageBox.StandardButton.No)==QMessageBox.StandardButton.Yes:
            self.memory.clear();self.chat.clear();self.refresh_memory()
    def make_settings(self):
        v=self.page();heading(v,'Settings & privacy','API keys use the OS credential store. Voice quality depends on your model and installed voices.')
        scroll=QScrollArea();scroll.setWidgetResizable(True);body=QWidget();form=QFormLayout(body);scroll.setWidget(body);v.addWidget(scroll)
        self.fields={}
        specs=[('endpoint','Model base URL','https://api.openai.com/v1'),('model','Model name','gpt-4o-mini'),('whisper_path','Local faster-whisper model directory',''),('stt_model','Remote STT model','whisper-1'),('tts_endpoint','External TTS URL (full /audio/speech path)',''),('tts_model','TTS model','tts-1'),('voice','Voice ID (installed system voice or external ID)','')]
        for key,label,default in specs:
            field=QLineEdit(self.memory.get(key,default));form.addRow(label,field);self.fields[key]=field
        self.key=QLineEdit();self.key.setEchoMode(QLineEdit.EchoMode.Password);self.key.setPlaceholderText('Leave blank to retain stored key');form.addRow('API key',self.key)
        self.enabled=QCheckBox('Enable configured model');self.enabled.setChecked(self.memory.get('model_enabled',False));form.addRow(self.enabled)
        self.automation=QCheckBox('Enable approved desktop automation');self.automation.setChecked(self.memory.get('automation',False));form.addRow(self.automation)
        self.rtl=QCheckBox('Kurdish RTL layout');self.rtl.setChecked(self.memory.get('rtl',False));form.addRow(self.rtl)
        self.stt=QComboBox();self.stt.addItems(['local','remote']);self.stt.setCurrentText(self.memory.get('stt_mode','local'));form.addRow('Speech recognition',self.stt)
        self.tts=QComboBox();self.tts.addItems(['text','system','external']);self.tts.setCurrentText(self.memory.get('tts','text'));form.addRow('Speech output',self.tts)
        self.speed=QSpinBox();self.speed.setRange(80,300);self.speed.setValue(self.memory.get('speed',170));form.addRow('Speech speed (system WPM)',self.speed)
        self.wake=QCheckBox('Require wake phrase in recorded transcripts');self.wake.setChecked(self.memory.get('wake',False));form.addRow(self.wake)
        note=QLabel('Wake mode checks transcribed recordings; it is not an always-listening wake detector.\nSorani STT and TTS are unvalidated until you test real Kurdish samples.\nSystem voices may have no Sorani voice. Text-only is the default.');note.setWordWrap(True);form.addRow(note)
        v.addWidget(button('Save settings',self.save_settings,True));v.addWidget(button('Remove stored API key',self.remove_key))
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft if self.rtl.isChecked() else Qt.LayoutDirection.LeftToRight)
    def save_settings(self):
        try:
            if self.key.text():Secrets.set(self.key.text());self.key.clear()
            for key,field in self.fields.items():self.memory.set(key,field.text().strip())
            for key,field in [('model_enabled',self.enabled),('automation',self.automation),('rtl',self.rtl),('wake',self.wake)]:self.memory.set(key,field.isChecked())
            self.memory.set('stt_mode',self.stt.currentText());self.memory.set('tts',self.tts.currentText());self.memory.set('speed',self.speed.value())
            self.setLayoutDirection(Qt.LayoutDirection.RightToLeft if self.rtl.isChecked() else Qt.LayoutDirection.LeftToRight)
            if self.speech:self.speech.model=None
            QMessageBox.information(self,'Settings','Settings saved locally.')
        except Exception as exc:QMessageBox.warning(self,'Settings',str(exc))
    def remove_key(self):
        if QMessageBox.question(self,'Remove key','Remove the API key from the OS credential store?')==QMessageBox.StandardButton.Yes:
            try:Secrets.set('')
            except Exception as exc:QMessageBox.warning(self,'Credentials',str(exc))
    def get_speech(self):
        if self.speech is None:
            from .speech import Speech
            self.speech=Speech(self.memory,self.guard,self.bridge.level.emit)
        return self.speech
    def toggle_mute(self):
        try:
            speech=self.get_speech();speech.muted=not speech.muted
            if speech.muted:self.interrupt()
            self.mic.setText('Microphone muted' if speech.muted else 'Microphone enabled');self.metrics()
        except Exception as exc:self.log(str(exc))
    def record_voice(self):
        try:
            speech=self.get_speech()
            if not self.recording:
                if self.busy:return
                speech.start();self.recording=True;self.record.setText('■ Finish recording');self.orb.active=True
                QTimer.singleShot(30000,self.finish_recording)
            else:self.finish_recording()
        except Exception as exc:self.log(str(exc))
    def finish_recording(self):
        if not self.recording:return
        self.recording=False;self.record.setText('● Record')
        def received(text):
            from .speech import wake_match
            if self.memory.get('wake',False) and not wake_match(text):self.log('Wake phrase was not detected.');return
            self.entry.setText(text);self.log('Transcript ready. Review and press Send.');self.navigate(0)
        self.run(self.speech.end,received)
    def speak_last(self):
        history=self.memory.history()
        last=next((r['content'] for r in reversed(history) if r['role']=='assistant'),'')
        if last:
            try:self.run(lambda:self.get_speech().say(last))
            except Exception as exc:self.log(str(exc))
    def interrupt(self):
        if self.speech:self.speech.stop()
        self.recording=False;self.record.setText('● Record');self.orb.level=0
    def audio_level(self,value):self.orb.level=value
    def metrics(self):
        s=self.tools.system();self.status.setText(f'● SYSTEM ONLINE     CPU {s["cpu"]:.0f}%     RAM {s["ram"]:.0f}%     •     MODEL {"CONFIGURED" if self.memory.get("model_enabled",False) else "OFF"}     •     MIC {"ON" if self.speech and not self.speech.muted else "MUTED"}')
    def stop(self):
        self.tools.stop();self.interrupt()
        for r in self.pending[:]:
            r['allowed']=False;r['done'].set();r['dialog'].reject()
        self.task.setText('■ Emergency stop active');self.log('Stopped managed processes and audio. In-flight HTTP requests cannot be recalled; results will be discarded.')
    def resume(self):
        if self.busy:self.log('Wait for the stopped task to finish before resuming.');return
        self.guard.stopped.clear();self.task.setText('● Ready • local workspace protected')
    def wizard(self):
        d=QDialog(self);d.setWindowTitle('Welcome • بەخێربێیت');v=QVBoxLayout(d)
        heading(v,'SHEIKH HAMAMOMIN AI','Your local desktop assistant.\n1. Chat works with an OpenAI-compatible endpoint or Ollama /v1.\n2. Configure a model and key in Settings. Each request asks approval.\n3. Desktop actions are disabled until enabled.\n4. Voice needs optional packages and a downloaded model or speech service.\n5. Kurdish voice quality must be tested with your own real samples.\nMemory and generated projects stay local unless you approve sending data.')
        v.addWidget(QLabel('Workspace: '+str(self.guard.workspace)))
        buttons=QDialogButtonBox(QDialogButtonBox.StandardButton.Ok);buttons.accepted.connect(d.accept);v.addWidget(buttons)
        if d.exec():self.memory.set('setup',True)
    def closeEvent(self,event):
        if self.busy:
            self.stop();QMessageBox.information(self,'Task stopping','Wait for the active task to finish before closing. Network timeouts are at most 90 seconds.');event.ignore();return
        self.tools.stop();self.interrupt();event.accept()
