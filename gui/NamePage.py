from os                 import path
from .MenuPage          import MenuPage , ColorIconButton
from PyQt5.QtCore       import Qt , pyqtSlot , pyqtSignal
from PyQt5.QtWidgets    import ( QLabel , QPushButton , QFrame , QSizePolicy ,
                                 QFormLayout , QHBoxLayout , QLineEdit , QWidget )

class NamePage( MenuPage ):
    CDIR   = path.dirname( path.abspath(__file__) )
    REPEAT = f"{CDIR}/images/repeat.svg"
    ABOUT  = f"{CDIR}/images/about.svg"
    CANCEL = f"{CDIR}/images/cancel.svg"

    WREPEAT = f"{CDIR}/images/w_repeat.svg"
    WABOUT  = f"{CDIR}/images/w_about.svg"
    WCANCEL = f"{CDIR}/images/w_cancel.svg"
    def __init__( self , backP = None , nextP = None , parent = None ):
        super().__init__( backP    = backP  ,
                          nextP    = nextP  ,
                          parent   = parent ,
                          subTitle = "Step 1: Choose a Name" )
        # Middle (Label & Line-Edit):
        self.nameWidg  = QWidget()
        self.nameForm  = QFormLayout( self.nameWidg )
        self.nameLabel = QLabel( "Name" )
        self.nameLine  = QLineEdit( "Border" )
        self.nameForm.setWidget( 0 , QFormLayout.LabelRole , self.nameLabel )
        self.nameForm.setWidget( 0 , QFormLayout.FieldRole , self.nameLine )

        # Debug mode:
        self.debug  = False
        self.dbgbut = ColorIconButton( "Debug: Off" , True )
        self.dbgbut.setChecked( False )
        self.nameForm.setWidget( 1 , QFormLayout.FieldRole , self.dbgbut )

        # Bottom:
        self.hline     = QFrame()
        self.hline.setFrameShape ( QFrame.HLine  )
        self.hline.setFrameShadow( QFrame.Sunken )

        self.previous  = ColorIconButton( "Use Previous Recipe" , False , NamePage.REPEAT , NamePage.WREPEAT ,icon_size = (32,32) )
        self.info      = ColorIconButton( "About"               , False , NamePage.ABOUT  , NamePage.WABOUT  ,icon_size = (32,32) )
        self.cancel    = ColorIconButton( "Cancel"              , False , NamePage.CANCEL , NamePage.WCANCEL ,icon_size = (32,32) )

        self.wbottom   = QWidget()
        self.lbottom   = QHBoxLayout( self.wbottom )
        self.lbottom.addWidget( self.info   )
        self.lbottom.addWidget( self.cancel )
        self.lbottom.setStretch( 0 , 0 )
        self.lbottom.setContentsMargins( 0 , 0 , 0 , 0 )

        # Layout Setup:
        self.layout.addWidget( self.nameWidg , 0 , Qt.AlignBottom )
        self.layout.addWidget( self.hline    )
        self.layout.addWidget( self.previous )
        self.layout.addWidget( self.wbottom  )

        self.dbgbut.toggled.connect( self.toggle_debug )

    @pyqtSlot()
    def toggle_debug( self ):
        self.debug = not self.debug
        if self.debug: self.dbgbut.setText( "Debug: On ")
        else:          self.dbgbut.setText( "Debug: Off ")

    def getData( self ):
        return { "debug" : self.debug ,
                 "name"  : self.nameLine.text() }
