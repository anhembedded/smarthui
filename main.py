import argparse
from ui_factory import QtWidgetsFactory, QMLFactory

def main():
    parser = argparse.ArgumentParser(description="SmartHui Application Runner")
    parser.add_argument("--ui", type=str, default="QtWidgets", help="Specify the UI type to run (e.g., QtWidgets, QML)")
    args = parser.parse_args()

    if args.ui.lower() == "qml":
        factory = QMLFactory()
    else:
        factory = QtWidgetsFactory()
    
    ui = factory.create_ui()
    ui.run()

if __name__ == "__main__":
    main()
