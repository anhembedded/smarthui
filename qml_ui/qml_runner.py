import sys
from pathlib import Path
from PySide6.QtCore import QObject
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtWidgets import QApplication

from qml_ui.backend_controller import BackendController

def run_qml_ui():
    app = QApplication.instance() or QApplication(sys.argv)
    engine = QQmlApplicationEngine()

    # Create and register the backend controller
    backend = BackendController()
    engine.rootContext().setContextProperty("backend", backend)

    # Add the directory containing the QML files to the import path
    qml_dir = Path(__file__).parent
    engine.addImportPath(str(qml_dir))

    qml_file = qml_dir / "Main.qml"
    engine.load(qml_file)

    if not engine.rootObjects():
        sys.exit(-1)

    sys.exit(app.exec())
