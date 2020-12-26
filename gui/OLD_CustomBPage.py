from PyQt5.QtWidgets import QWidget , QHBoxLayout , QPushButton , QLineEdit , QLabel
from PyQt5.QtCore    import pyqtSlot , pyqtSignal

from .Page import Page
from .MethodDisplay import MethodWidget

class OptButtons( QWidget ):
    clearRequest = pyqtSignal()
    addRequest   = pyqtSignal()
    remRequest   = pyqtSignal()
    def __init__( self , parent = None ):
        super().__init__( parent )
        self.layout = QHBoxLayout()
        self.setLayout( self.layout )

        self.clear = QPushButton( "Clear"  )
        self.add   = QPushButton( "Add"    )
        self.rem   = QPushButton( "Remove" )

        self.layout.addWidget( self.clear )
        self.layout.addWidget( self.rem   )
        self.layout.addWidget( self.add   )

        self.clear.released.connect( self.__clear_request__ )
        self.add.released.connect( self.__add_request__ )
        self.rem.released.connect( self.__rem_request__ )

    @pyqtSlot()
    def __clear_request__( self ):
        self.clearRequest.emit()

    @pyqtSlot()
    def __add_request__( self ):
        self.addRequest.emit()

    @pyqtSlot()
    def __rem_request__( self ):
        self.remRequest.emit()

class CustomBPage( Page ):
    def __init__( self , prevP = None , nextP = None , parent = None ):
        super().__init__( prevP , nextP , parent )
        table = MethodWidget()
        bttns = OptButtons()
        self.includeWidget( table , "table"   )
        self.includeWidget( bttns , "buttons" )

        bttns.clearRequest.connect( self.reset )
        bttns.addRequest.connect( self.add )
        bttns.remRequest.connect( self.rem )

    def reset( self ):
        table = self.getWidget( "table" )
        first = [ table.getUnsafeData()[0] ]
        table.setRecipe( first )

    def add( self ):
        table = self.getWidget( "table" )
        table.addMethod()

    def rem( self ):
        table = self.getWidget( "table" )
        table.removeMethod()

    def getData( self ):
        t = self.getWidget( "table" )
        return { "methoddsc" : t.getData() }

