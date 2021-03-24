# Module:   gui.QuickPage.py | [ Language Python ]
# Author:   Gaps | sGaps | ArtGaps
# LICENSE:  GPLv3 (available in ./LICENSE.txt)
# -------------------------------------------------
"""
    Defines the Quick page of the Smart Menu.

    [:] Defined in this module
    --------------------------
    QuickPage :: class
        Allows user to make its onw simple recipe-

    [*] Author
     |- Gaps : sGaps : ArtGaps
"""
from PyQt5.QtCore       import pyqtSlot , pyqtSignal

from .MenuPage          import MenuPage
from .MethodDisplay     import MethodWidget

class QuickPage( MenuPage ):
    """ Allows user to make its own simple recipe. """
    def __init__( self , backP = None , nextP = None , parent = None ):
        super().__init__( backP    = backP  ,
                          nextP    = nextP  ,
                          parent   = parent ,
                          subTitle = "Step 4: Border Recipe" )
        self.table  = MethodWidget()
        # Layout Setup:
        self.layout.addWidget( self.table )

    def getData( self ):
        return { "q-recipedsc" : self.table.getData() }
