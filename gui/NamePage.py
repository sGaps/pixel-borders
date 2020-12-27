from MenuPage           import MenuPage
from PyQt5.QtCore       import Qt
from PyQt5.QtWidgets    import ( QVBoxLayout , QLabel , QPushButton ,
                                 QFrame , QFormLayout , QLineEdit , QWidget )


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
        self.cancel    = QPushButton( "Cancel" )

        # Layout Setup:
        #self.layout.addWidget( self.subTitle )
        self.layout.addWidget( self.nameWidg , 0 , Qt.AlignBottom )
        self.layout.addWidget( self.hline    )
        self.layout.addWidget( self.cancel   )
        self.layout.addWidget( self.previous )

    def getData( self ):
        return { "name" : self.nameLine.text() }
