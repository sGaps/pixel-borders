from PyQt5.QtCore       import pyqtSlot , pyqtSignal
from PyQt5.QtWidgets    import QVBoxLayout , QHBoxLayout , QLabel , QPushButton

from MenuPage           import MenuPage
from MethodDisplay      import MethodWidget

class CustomPage( MenuPage ):
    def __init__( self , backP = None , nextP = None , parent = None ):
        super().__init__( backP    = backP  ,
                          nextP    = nextP  ,
                          parent   = parent ,
                          subTitle = "Step 4: Border Type" )
        #self.layout   = QVBoxLayout( self )

        #self.subTitle = subTitleLabel( "Step 4: Border Type" )

        self.table  = MethodWidget()
        self.bottom = QHBoxLayout()
        self.add    = QPushButton( "Add"    )
        self.clr    = QPushButton( "Clear"  )
        self.rem    = QPushButton( "Remove" )

        self.bottom.addWidget( self.clr )
        self.bottom.addWidget( self.rem )
        self.bottom.addWidget( self.add )

        # Layout Setup:
        #self.layout.addWidget( self.subTitle )
        self.layout.addWidget( self.table    )
        self.layout.addLayout( self.bottom   )
