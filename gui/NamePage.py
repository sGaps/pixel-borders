from MenuPage           import MenuPage
from PyQt5.QtCore       import Qt
from PyQt5.QtWidgets    import ( QLabel , QPushButton , QFrame , QSizePolicy ,
                                 QFormLayout , QHBoxLayout , QLineEdit , QWidget )


class NamePage( MenuPage ):
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

        self.previous  = QPushButton( "Use Previous Recipe" )
        self.info      = QPushButton( "About"  )
        self.cancel    = QPushButton( "Cancel" )

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
