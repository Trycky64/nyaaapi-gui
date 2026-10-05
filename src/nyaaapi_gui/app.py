from __future__ import annotations

import sys

from PySide6.QtWidgets import QApplication

from . import __version__
from .main_window import MainWindow


def main() -> int:
    """Start the NyaaAPI GUI event loop."""
    app = QApplication.instance() or QApplication(sys.argv)
    app.setApplicationName("NyaaAPI GUI")
    app.setApplicationVersion(__version__)
    window = MainWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
