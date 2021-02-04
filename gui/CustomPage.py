from PyQt5.QtCore       import pyqtSlot , pyqtSignal
from PyQt5.QtWidgets    import QHBoxLayout , QPushButton

from .MenuPage          import MenuPage
from .MethodDisplay     import MethodWidget

class CustomPage( MenuPage ):
    def __init__( self , backP = None , nextP = None , parent = None ):
        super().__init__( backP    = backP  ,
                          nextP    = nextP  ,
                          parent   = parent ,
                          subTitle = "Step 4: Border Recipe" )

        self.table  = MethodWidget()
        self.bottom = QHBoxLayout()
        self.add    = QPushButton( "Add"    )
        self.clr    = QPushButton( "Clear"  )
        self.rem    = QPushButton( "Remove" )

        self.bottom.addWidget( self.clr )
        self.bottom.addWidget( self.rem )
        self.bottom.addWidget( self.add )

        # Layout Setup:
        self.layout.addWidget( self.table    )
        self.layout.addLayout( self.bottom   )

        # Connections:
        self.add.clicked.connect( self.addMethodIntoRecipe )
        self.clr.clicked.connect( self.clearRecipe         )
        self.rem.clicked.connect( self.removeFromRecipe    )

    @pyqtSlot()
    def clearRecipe( self ):
        self.table.setRecipe( self.table.getUnsafeData()[:1] )

    @pyqtSlot()
    def addMethodIntoRecipe( self ):
        self.table.addMethod()

    @pyqtSlot()
    def removeFromRecipe( self ):
        self.table.removeMethod()

    def getData( self ):
        return { "c-recipedsc" : self.table.getData() }
