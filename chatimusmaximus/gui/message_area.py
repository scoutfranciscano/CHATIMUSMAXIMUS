from datetime import datetime
import queue
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtCore import Qt

class _StandardTextFormat(QtGui.QTextCharFormat):
    """
    Standard text format for `MessageArea`
    """
    def __init__(self, text_color=Qt.white, font=QtGui.QFont.DemiBold):
        super(_StandardTextFormat, self).__init__()
        self.setFontWeight(font)
        self.setForeground(text_color)
        self.setFontPointSize(13)

class _Reciever(QtCore.QObject):
    text_signal = QtCore.pyqtSignal(str, str, str)
    def __init__(self, parent=None):
        super(_Reciever, self).__init__(parent)
        self.queue = queue.Queue()

    @QtCore.pyqtSlot(str, str, str)
    def chat_slot(self, sender, message, platform):
        self.queue.put([sender, message, platform])
        self.run()
    
    def run(self):
        item = self.queue.get()
        self.text_signal.emit(*item)


class MessageArea(QtWidgets.QTextEdit):
    time_signal = QtCore.pyqtSignal(str)
    def __init__(self, parent=None):
        super(MessageArea, self).__init__(parent)
        self.setReadOnly(True)
        self.text_format = _StandardTextFormat(font=self.fontWeight())

        self._reciever = _Reciever()
        self._reciever.text_signal.connect(self.insert_text)
        self.chat_slot = self._reciever.chat_slot
        
        # styling
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.viewport().setAutoFillBackground(False)

        self.name_formats = {} 

    def set_color(self, color, platform):
        if platform in self.name_formats:
            format = self.name_formats[platform]
            format.setForeground(QtGui.QColor(color))
        else:
            self.name_formats[platform] = _StandardTextFormat(QtGui.QColor(color))
    
    @QtCore.pyqtSlot(str, str, str)
    def insert_text(self, sender, message, platform):
        # get the timestamp
        formatted_datetime = datetime.now().strftime("%H:%M:%S")
        self.time_signal.emit(formatted_datetime)

        self._insert_and_format(sender, message, platform)
        # get scroll bar and set to maximum
        scroll_bar = self.verticalScrollBar()
        scroll_bar.setValue(scroll_bar.maximum())

    def _insert_and_format(self, sender, message, platform):
        """
        Helper method to handle the text display logic
        """
        # get cursor
        cursor = self.textCursor()
        # set the format to the name format
        cursor.setCharFormat(self.name_formats[platform])
        # the platform name is in a bracket. Example: `[Youtube]:`
        bracket_string = ' [{}]: '.format(platform.title())
        # inserts the sender name next to the platform & timestamp
        cursor.insertText(sender + bracket_string)
        # sets format to text format
        cursor.setCharFormat(self.text_format)
        # inserts message
        cursor.insertText(message)
        # inserts newline
        cursor.insertBlock()
        cursor.movePosition(QtGui.QTextCursor.End, QtGui.QTextCursor.MoveAnchor)
        self.setTextCursor(cursor)
