import os
import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QIcon
from trafficlab.gui.main_window import MainWindow


def main():
    backend_root = os.path.dirname(os.path.abspath(__file__))
    os.chdir(backend_root)
    app = QApplication(sys.argv)

    app.setWindowIcon(QIcon(os.path.join(backend_root, "media", "icon.png")))

    try:
        import qdarktheme
        if hasattr(qdarktheme, 'setup_theme'):
            qdarktheme.setup_theme("dark")
        else:
            app.setStyleSheet(qdarktheme.load_stylesheet("dark"))
    except Exception:
        pass

    # Start voice agent server in background thread
    try:
        from voice_agent_server import start_voice_agent_server
        start_voice_agent_server()
    except Exception as e:
        print(f"[VoiceAgent] Failed to start: {e}")

    win = MainWindow()
    win.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
