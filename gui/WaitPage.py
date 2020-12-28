from .MenuPage          import SinkPage
from PyQt5.QtCore       import Qt , pyqtSlot , pyqtSignal
from PyQt5.QtWidgets    import QPushButton , QProgressBar , QVBoxLayout

class WaitPage( SinkPage ):
    def __init__( self , parent = None ):
        super().__init__( parent , "Step 5: Wait for the border" )

        self.cancel   = QPushButton( "Cancel" )
        self.info     = QPushButton( "About"  )
        self.progress = QProgressBar()

        self.layout.addWidget( self.progress , 1 , Qt.AlignTop )
        self.layout.addWidget( self.info   )
        self.layout.addWidget( self.cancel )
