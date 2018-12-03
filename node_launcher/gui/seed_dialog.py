from PySide2.QtWidgets import QDialog, QTextBrowser


class SeedDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Mnemonic')
        self.text = QTextBrowser(self)
