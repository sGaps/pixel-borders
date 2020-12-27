from PyQt5.QtCore       import pyqtSlot , pyqtSignal

from MenuPage           import MenuPage
from MethodDisplay      import MethodWidget

# TODO: Specialize getData(...) Method!
class QuickPage( MenuPage ):
    def __init__( self , backP = None , nextP = None , parent = None ):
        super().__init__( backP    = backP  ,
                          nextP    = nextP  ,
                          parent   = parent ,
                          subTitle = "Step 4: Border Type" )
        self.table  = MethodWidget()
        # Layout Setup:
        self.layout.addWidget( self.table )
