from MenuPage           import MenuPage , subTitleLabel
from PyQt5.QtCore       import Qt
from PyQt5.QtWidgets    import QVBoxLayout , QLabel , QPushButton , QFrame , QFormLayout , QLineEdit


class NamePage( MenuPage ):
    def __init__( self , backP = None , nextP = None , parent = None ):
        super().__init__( backP , nextP , parent )
        self.layout = QVBoxLayout( self )

        self.subTitle = subTitleLabel( "Step 1: Choose a Name" )

        # Middle (Label)
        self.nameForm  = QFormLayout()
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
        self.layout.addWidget( self.subTitle )
        self.layout.addLayout( self.nameForm )
        self.layout.addWidget( self.hline    )
        self.layout.addWidget( self.cancel   )
        self.layout.addWidget( self.previous )

    def getData( self ):
        return { "name" : self.nameLine.text() }
