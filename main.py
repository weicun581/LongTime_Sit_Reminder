import pathlib
import sys

from PyQt5.QtWidgets import QApplication

from app_controller import AppController


def main():
    app = QApplication(sys.argv)
    controller = AppController(app=app, base_dir=pathlib.Path(__file__).resolve().parent)
    if not controller.start():
        return 1
    return app.exec_()


if __name__ == "__main__":
    sys.exit(main())
