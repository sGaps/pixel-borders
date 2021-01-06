from .MenuPage          import SinkPage
from PyQt5.QtCore       import Qt , pyqtSlot , pyqtSignal
from PyQt5.QtWidgets    import QPushButton , QProgressBar , QLabel , QStackedWidget , QVBoxLayout
from PyQt5.QtGui        import QFont

class WaitPage( SinkPage ):
    def __init__( self , parent = None ):
        super().__init__( parent , "Step 5: Wait for the border" )

        self.cancel   = QPushButton( "Cancel" )
        self.info     = QPushButton( "About"  )
        self.progress = QProgressBar()

        font          = QFont()
        font.setBold  ( True )
        font.setItalic( True )

        self.dbgMSG   = QLabel()
        self.accept   = QPushButton( "Ok" )
        self.bottom   = QStackedWidget()
        self.accept.setFont( font )

        self.bottom.addWidget( self.cancel )
        self.bottom.addWidget( self.accept )
        self.raiseCancel()

        self.layout.addWidget( self.progress , 1 , Qt.AlignTop )
        self.layout.addWidget( self.dbgMSG )
        self.layout.addWidget( self.info   )
        self.layout.addWidget( self.bottom )

    def raiseCancel( self ):
        self.bottom.setCurrentWidget( self.cancel )

    def raiseAccept( self ):
        self.bottom.setCurrentWidget( self.accept )

