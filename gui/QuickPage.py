from PyQt5.QtCore       import pyqtSlot , pyqtSignal
from PyQt5.QtWidgets    import QVBoxLayout , QHBoxLayout , QLabel , QPushButton

from MenuPage           import MenuPage , subTitleLabel
from MethodDisplay      import MethodWidget

class QuickPage( MenuPage ):
    def __init__( self , backP = None , nextP = None , parent = None ):
        super().__init__( backP , nextP , parent )
        self.layout   = QVBoxLayout( self )

        self.subTitle = subTitleLabel( "Step 4: Border Type" )
        self.table  = MethodWidget()

        # Layout Setup:
        self.layout.addWidget( self.subTitle )
        self.layout.addWidget( self.table    )
