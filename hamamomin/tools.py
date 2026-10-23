import os
import shutil
import subprocess
import threading
import webbrowser
from pathlib import Path
from urllib.parse import urlparse
import psutil
from .security import Denied


class Tools:
    COMMANDS = {'install': ['npm', 'install', '--ignore-scripts', '--no-audit', '--no-fund'], 'build': ['npm', 'run', 'build'], 'test': ['npm', 'test', '--', '--run'], 'preview': ['npm', 'run', 'dev', '--', '--host', '127.0.0.1'], 'git-init': ['git', 'init'], 'git-status': ['git', 'status', '--short']}

    def __init__(self, guard, output=lambda s: None):
        self.guard, self.output = guard, output
        self.processes = []
        self.lock = threading.Lock()

    def vscode(self):
        candidates = [shutil.which('code.exe'), shutil.which('code')]
        if os.name == 'nt':
            candidates += [str(Path(os.getenv('LOCALAPPDATA', '')) / 'Programs/Microsoft VS Code/Code.exe'), str(Path(os.getenv('ProgramFiles', 'C:/Program Files')) / 'Microsoft VS Code/Code.exe')]
        return next((p for p in candidates if p and Path(p).is_file()), None)

    def launch(self, app, project=None):
        self.guard.approve('Open application', f'{app}\n{project or ""}', desktop=True)
        if app == 'vscode':
            exe = self.vscode()
            if not exe:
                raise FileNotFoundError('VS Code not found. Install it with the code CLI or use the standard Windows location.')
            args = [exe] + ([str(self.guard.path(project))] if project else [])
        elif app in ('notepad', 'explorer') and os.name == 'nt':
            args = [str(Path(os.environ['WINDIR']) / 'System32' / (app + '.exe'))]
            if app == 'explorer':
                args.append(str(self.guard.workspace))
        elif app == 'chrome' and os.name == 'nt':
            exe = next((p for p in [Path(os.getenv('ProgramFiles', 'C:/Program Files')) / 'Google/Chrome/Application/chrome.exe', Path(os.getenv('LOCALAPPDATA', '')) / 'Google/Chrome/Application/chrome.exe'] if p.is_file()), None)
            if not exe:
                raise FileNotFoundError('Chrome not found in standard locations.')
            args = [str(exe)]
        else:
            raise Denied('Unsupported application on this platform.')
        if Path(args[0]).suffix.lower() in ('.cmd', '.bat'):
            raise Denied('Batch launchers are not allowed. Install the native VS Code executable.')
        subprocess.Popen(args, shell=False)
        self.guard.memory.event('launch', app)
        return f'Launched {app}.'

    def website(self, url):
        p = urlparse(url)
        if p.scheme not in ('https', 'http') or not p.hostname or p.username or p.password:
            raise Denied('Only HTTP(S) URLs without embedded credentials are allowed.')
        self.guard.approve('Open URL', url, desktop=True)
        webbrowser.open(url)
        return 'Browser open requested.'

    def system(self):
        return {'cpu': psutil.cpu_percent(), 'ram': psutil.virtual_memory().percent}

    def search(self, query):
        if not query or len(query) > 100:
            raise ValueError('Enter a filename fragment.')
        found = []
        for root, dirs, files in os.walk(self.guard.workspace, followlinks=False):
            self.guard.check()
            dirs[:] = [d for d in dirs if d not in ('node_modules', '.git', '.venv') and not (Path(root)/d).is_symlink()]
            for f in files:
                if query.casefold() in f.casefold():
                    p = Path(root)/f
                    if p.resolve().is_relative_to(self.guard.workspace):
                        found.append(str(p.relative_to(self.guard.workspace)))
                if len(found) >= 100:
                    return '\n'.join(found)
        return '\n'.join(found) or 'No matching files.'

    def screenshot(self):
        self.guard.approve('Screenshot', 'Save the entire screen in the local assistant workspace.', desktop=True)
        import pyautogui
        p = self.guard.path('screenshot.png')
        if p.exists():
            self.guard.approve('Overwrite screenshot', str(p))
        pyautogui.screenshot().save(p)
        return str(p)

    def media(self):
        self.guard.approve('Media play / pause', 'Send the Windows play/pause media key.', desktop=True)
        import pyautogui
        pyautogui.press('playpause')
        return 'Media key sent.'

    def command(self, name, project):
        if name not in self.COMMANDS:
            raise Denied('Command is not allowlisted.')
        cwd = self.guard.path(project)
        if not cwd.is_dir():
            raise ValueError('Project directory does not exist.')
        args = self.COMMANDS[name].copy()
        self.guard.approve('Run project command', f'Folder: {cwd}\nCommand: {" ".join(args)}\nBuild, test, and preview scripts execute project code. npm install contacts the registry; lifecycle scripts are disabled.')
        executable = shutil.which(args[0])
        if not executable:
            raise FileNotFoundError(f'{args[0]} is not installed.')
        # Invoke npm's JS entrypoint with node on Windows, never cmd.exe.
        if os.name == 'nt' and args[0] == 'npm':
            node = shutil.which('node.exe')
            cli = Path(executable).parent / 'node_modules/npm/bin/npm-cli.js'
            if not node or not cli.is_file():
                raise FileNotFoundError('A standard Node.js installation is required.')
            args = [node, str(cli), *args[1:]]
        else:
            args[0] = executable
        with self.lock:
            self.guard.check()
            proc = subprocess.Popen(args, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, errors='replace', shell=False, start_new_session=os.name != 'nt')
            self.processes.append(proc)
        # A timer bounds foreground commands and preview lifetime. Stop kills descendants.
        timer = threading.Timer(600 if name == 'preview' else 180, lambda: self._kill(proc))
        timer.start()
        try:
            for line in proc.stdout:
                self.guard.check()
                self.output(line.rstrip())
            code = proc.wait()
            self.guard.memory.event('command', f'{name}: exit {code}; project={project}')
            return f'{name} finished with exit code {code}.'
        finally:
            timer.cancel()
            with self.lock:
                if proc in self.processes:
                    self.processes.remove(proc)
            if proc.poll() is None:
                self._kill(proc)

    @staticmethod
    def _kill(proc):
        try:
            parent = psutil.Process(proc.pid)
            for child in reversed(parent.children(recursive=True)):
                try:
                    child.kill()
                except psutil.Error:
                    pass
            parent.kill()
        except psutil.Error:
            pass

    def stop(self):
        self.guard.stopped.set()
        with self.lock:
            for proc in self.processes:
                self._kill(proc)
