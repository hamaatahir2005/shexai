import threading
from pathlib import Path


class Denied(RuntimeError):
    pass


class Guard:
    def __init__(self, workspace, memory, confirm):
        self.workspace = Path(workspace).resolve()
        self.workspace.mkdir(parents=True, exist_ok=True)
        self.memory, self.confirm = memory, confirm
        self.stopped = threading.Event()

    def check(self):
        if self.stopped.is_set():
            raise Denied('Emergency stop is active. Resume explicitly before starting another task.')

    def path(self, relative):
        self.check()
        p = (self.workspace / relative).resolve()
        if not p.is_relative_to(self.workspace) or p == self.workspace:
            raise Denied('Path must be inside the assistant workspace.')
        # Windows alternate data streams / special device names are forbidden on every platform.
        for part in p.relative_to(self.workspace).parts:
            if ':' in part or part.rstrip('. ').split('.')[0].upper() in {'CON','PRN','AUX','NUL', *[f'COM{i}' for i in range(1,10)], *[f'LPT{i}' for i in range(1,10)]}:
                raise Denied('Unsafe Windows filename.')
        return p

    def approve(self, action, detail, desktop=False):
        self.check()
        if desktop and not self.memory.get('automation', False):
            raise Denied('Desktop automation is disabled in Settings.')
        allowed = bool(self.confirm(action, detail))
        self.memory.event('permission', f'{action}: {"approved" if allowed else "denied"}')
        self.check()
        if not allowed:
            raise Denied('Permission declined.')


class Secrets:
    @staticmethod
    def get():
        import keyring
        import os
        return keyring.get_password('SheikhHamamomin', 'api_key') or os.getenv('HAMAMOMIN_API_KEY', '')

    @staticmethod
    def set(value):
        import keyring
        if value:
            keyring.set_password('SheikhHamamomin', 'api_key', value)
        else:
            try:
                keyring.delete_password('SheikhHamamomin', 'api_key')
            except keyring.errors.PasswordDeleteError:
                pass
