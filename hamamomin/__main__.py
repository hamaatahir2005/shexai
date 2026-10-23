import sys
from pathlib import Path
from dotenv import load_dotenv
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon
from .ui import Window


def main():
    if '--self-test' in sys.argv:
        from .package_probe import probe
        report=Path(sys.executable).parent.parent/'windows-self-test.json' if getattr(sys,'frozen',False) else Path.cwd()/'windows-self-test.json'
        sys.exit(probe(report))
    load_dotenv()
    app=QApplication(sys.argv)
    app.setApplicationName('SHEIKH HAMAMOMIN AI')
    app.setOrganizationName('Hamamomin')
    icon=Path(getattr(sys,'_MEIPASS',Path(__file__).parent.parent))/'assets'/'icon.ico'
    if icon.exists():app.setWindowIcon(QIcon(str(icon)))
    window=Window();window.show()
    sys.exit(app.exec())

if __name__=='__main__':main()
