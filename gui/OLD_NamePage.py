from PyQt5.QtWidgets import QWidget , QFormLayout , QPushButton , QLineEdit
from PyQt5.QtCore    import pyqtSlot , pyqtSignal
from .Page import Page

class NameContents( QWidget ):
    def __init__( self , parent = None ):
        super().__init__( parent )
        # Layout setup:
        self.layout = QFormLayout()
        self.setLayout( self.layout )

        # Widgets setup:
        self.line   = QLineEdit()
        self.layout.addRow( "Name" , self.line )

    def name():
        return self.line.text()


class NamePage( Page ):
    loadRequest = pyqtSignal()
    def __init__( self , prevP = None , nextP = None , parent = None ):
        super().__init__( prevP , nextP , parent )
        load = QPushButton( "Use Previous Recipe" )
        self.includeWidget( NameContents() , "name" )
        self.includeWidget( load           , "load" )

        load.released.connect( self.__load_request__ )

    @pyqtSlot()
    def __load_request__( self ):
        self.loadRequest.emit()

    def getData( self ):
        w = self.getWidget( "name" )
        return { "name" : w.name() if w else "" }

