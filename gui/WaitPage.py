from os                 import path
from .MenuPage          import SinkPage , subTitleLabel , buttonWithIcon
from PyQt5.QtCore       import Qt , pyqtSlot , pyqtSignal
from PyQt5.QtWidgets    import QPushButton , QProgressBar , QLabel , QWidget , QStackedWidget , QVBoxLayout , QHBoxLayout
from PyQt5.QtGui        import QFont

class WaitPage( SinkPage ):
    CDIR   = path.dirname( path.abspath(__file__) )
    ABOUT  = f"{CDIR}/images/about.svg"
    CANCEL = f"{CDIR}/images/cancel.svg"
    OK     = f"{CDIR}/images/ok.svg"
    def __init__( self , parent = None ):
        super().__init__( parent , "Step 5: Wait for the border" )

        self.cancel    = buttonWithIcon( "Cancel" , False , WaitPage.CANCEL, icon_size = (32,32) )
        self.info      = buttonWithIcon( "About"  , False , WaitPage.ABOUT , icon_size = (32,32) )
        self.progress  = QProgressBar()
        self.fnum      = 0

        font          = QFont()
        font.setBold  ( True )
        font.setItalic( True )

        self.usrMSG   = QLabel()
        self.accept    = buttonWithIcon( "Ok" , False , WaitPage.OK , icon_size = (32,32) )
        self.bottom   = QStackedWidget()
        self.accept.setFont( font )

        self.bottom.addWidget( self.cancel )
        self.bottom.addWidget( self.accept )
        self.raiseCancel()

        # Detailed steps
        self.fstep  = subTitleLabel( "" )
        self.frame  = QLabel()
        self.subwid = QWidget()
        self.sublyt = QHBoxLayout( self.subwid )
        self.sublyt.addWidget( self.fstep , 0 , Qt.AlignLeft  | Qt.AlignTop )
        self.sublyt.addWidget( self.frame , 1 , Qt.AlignRight | Qt.AlignTop )
        self.sublyt.setSpacing( 0 )
        self.subwid.setContentsMargins( 0 , 0 , 0 , 0 )

        self.layout.addWidget( self.progress , 1 , Qt.AlignTop )
        self.layout.addWidget( self.subwid   , 2 , Qt.AlignTop )
        self.layout.addWidget( self.usrMSG )
        self.layout.addWidget( self.info   )
        self.layout.addWidget( self.bottom )

        # Tab Order:
        self.setTabOrder( self.accept , self.cancel )
        self.setTabOrder( self.accept , self.info   )
        self.setTabOrder( self.info   , self.cancel )

    def raiseCancel( self ):
        self.bottom.setCurrentWidget( self.cancel )

    def raiseAccept( self ):
        self.bottom.setCurrentWidget( self.accept )

    @pyqtSlot( int )
    def updateFrameNumber( self , n ):
        self.fnum = n
        self.frame.setText( f"{n}" )

    @pyqtSlot()
    def eraseFrameNumber( self ):
        self.frame.setText( f"" )

    @pyqtSlot()
    def incrementFrameNumber( self ):
        self.fnum += 1
        self.frame.setText( f"{self.fnum}" )

