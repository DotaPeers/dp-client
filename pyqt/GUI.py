import sys
import threading
import asyncio

from PyQt5 import QtWidgets, QtGui

from pyqt.MainWindow import Ui_mainWindow
from ProtoClient import ProtoClient


class ClientThread(threading.Thread):
    """
    Thread that handles the ProtoClient asyncio.
    """

    def __init__(self, gui: "MainWindow"):
        super().__init__()
        self.gui = gui
        self.client = ProtoClient(self.gui)
        self.eventLoop = asyncio.new_event_loop()

    def stop(self):
        """
        Brutally slaughter the eventloop
        """

        self.client.doRun = False
        self.eventLoop.stop()
        self.eventLoop.close()

    def run(self) -> None:
        self.eventLoop.run_until_complete(self.client.receiveMessages(self.gui.connectionId))


class MainWindow(QtWidgets.QMainWindow, Ui_mainWindow):
    """
    The GUI that gets opened
    """

    def __init__(self, *args, obj=None, **kwargs):
        super().__init__(*args, obj, **kwargs)
        self.setupUi(self)

        self.stackedWidget.setCurrentIndex(0)

        # Custom vars
        self.connectionId = None
        self.clientThread = ClientThread(self)

        # Connect Events
        self.connectButton.clicked.connect(self.onSubmitBtnClicked)

    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        """
        Called when the GUi gets closed
        """

        super().closeEvent(a0)
        self.clientThread.stop()

    def onSubmitBtnClicked(self):
        """
        Called when when the "Connect" button is pressed
        """

        inputText = self.idEdit.text()
        if inputText == None or inputText == "":
            self.errorLabel.setText("⚠️ ID can't be empty.")
            return

        self.errorLabel.clear()
        self.connectionId = inputText
        self.stackedWidget.setCurrentIndex(1)

        self.clientThread.start()

    def addToTextBrowser(self, toAdd):
        """
        Adds data to the TextBrowser and scrolls down
        """

        self.textBrowser.append(str(toAdd))
        sb = self.textBrowser.verticalScrollBar()
        sb.setValue(sb.maximum())



if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)

    window = MainWindow()
    window.show()
    app.exec()
