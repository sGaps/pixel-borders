from PyQt5.QtWidgets import QWidget , QFormLayout , QPushButton , QLineEdit , QLabel
from PyQt5.QtCore    import pyqtSlot , pyqtSignal

from .Page import Page
from .MethodDisplay import MethodWidget

class QuickBPage( Page ):
    def __init__( self , prevP = None , nextP = None , parent = None ):
        super().__init__( prevP , nextP , parent )
        self.includeWidget( MethodWidget() , "table" )

    def getData( self ):
        t = self.getWidget( "table" )
        return { "methoddsc" : t.getData() }

