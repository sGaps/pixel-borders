from PyQt5.QtWidgets import QWidget , QFormLayout , QPushButton , QLineEdit , QLabel
from PyQt5.QtCore    import pyqtSlot , pyqtSignal

from .Page import CancelPage

class ExitPage( CancelPage ):
    def __init__( self , parent = None ):
        super().__init__( parent )
        self.includeWidget( QLabel( "Closing Plugin...") , "exit" )

