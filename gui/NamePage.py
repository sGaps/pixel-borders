from os                 import path
from .MenuPage          import MenuPage , buttonWithIcon
from PyQt5.QtCore       import Qt
from PyQt5.QtWidgets    import ( QLabel , QPushButton , QFrame , QSizePolicy ,
                                 QFormLayout , QHBoxLayout , QLineEdit , QWidget )

class NamePage( MenuPage ):
    CDIR  = path.dirname( path.abspath(__file__) )
    REPEAT = f"{CDIR}/images/repeat.svg"
    ABOUT  = f"{CDIR}/images/about.svg"
    CANCEL = f"{CDIR}/images/cancel.svg"
    def __init__( self , backP = None , nextP = None , parent = None ):
        super().__init__( backP    = backP  ,
                          nextP    = nextP  ,
                          parent   = parent ,
                          subTitle = "Step 1: Choose a Name" )
        # Middle (Label)
        self.nameWidg  = QWidget()
        self.nameForm  = QFormLayout( self.nameWidg )
        self.nameLabel = QLabel( "Name" )
        self.nameForm.setWidget( 1 , QFormLayout.LabelRole , self.nameLabel )
        # Middle (QLineEdit)
        self.nameLine  = QLineEdit( "Border" )
        self.nameForm.setWidget( 1 , QFormLayout.FieldRole , self.nameLine )

        # Bottom:
        self.hline     = QFrame()
        self.hline.setFrameShape ( QFrame.HLine  )
        self.hline.setFrameShadow( QFrame.Sunken )

        self.previous  = buttonWithIcon( "Use Previous Recipe" , False , NamePage.REPEAT , icon_size = (32,32) )
        self.info      = buttonWithIcon( "About"               , False , NamePage.ABOUT  , icon_size = (32,32) )
        self.cancel    = buttonWithIcon( "Cancel"              , False , NamePage.CANCEL , icon_size = (32,32) )

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

    def getData( self ):
        return { "name" : self.nameLine.text() }
