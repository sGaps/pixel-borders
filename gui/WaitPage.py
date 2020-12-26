from PyQt5.QtWidgets import QWidget , QHBoxLayout , QPushButton , QProgressBar , QLabel
from PyQt5.QtCore    import pyqtSlot , pyqtSignal

from .Page import AcceptPage

class OptButtons( QWidget ):
    cancelRequest = pyqtSignal()
    infoRequest   = pyqtSignal()
    def __init__( self , parent = None ):
        super().__init__( parent )
        self.layout = QHBoxLayout()
        self.setLayout( self.layout )

        self.cancel = QPushButton( "Cancel"  )
        self.info   = QPushButton( "Information" )

        self.layout.addWidget( self.cancel )
        self.layout.addWidget( self.info )

    @pyqtSlot()
    def __cancel_request__( self ):
        self.cancelRequest.emit()

    @pyqtSlot()
    def __info_request__( self ):
        self.infoRequest.emit()

class WaitPage( AcceptPage ):
    def __init__( self , parent = None ):
        super().__init__( parent )
        self.includeWidget( QProgressBar() , "progress" )
        self.includeWidget( OptButtons()   , "options"  )

