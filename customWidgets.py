from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QDialog

from dialog import Ui_transferDialog


class Dialog(QDialog, Ui_transferDialog):
    startBtnClicked = pyqtSignal()
    cancelBtnClicked = pyqtSignal()

    def __init__(self, parent=None):
        super(Dialog, self).__init__(parent)
        self.setupUi(self)
        self.startBtn.clicked.connect(self.start)
        self.cancelBtn.clicked.connect(self.cancel)

    def start(self):
        self.startBtnClicked.emit()
        self.accept()

    def cancel(self):
        self.cancelBtnClicked.emit()
        self.reject()


if __name__ == '__main__':
    import sys
    from PyQt5.QtWidgets import QApplication

    app = QApplication(sys.argv)
    dialog = Dialog()
    dialog.show()
    sys.exit(app.exec_())
