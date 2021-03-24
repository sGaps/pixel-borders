# Module:   gui.ColorPage.py | [ Language Python ]
# Author:   Gaps | sGaps | ArtGaps
# LICENSE:  GPLv3 (available in ./LICENSE.txt)
# ------------------------------------------------
"""
    Defines the color page of the Smart Menu.

    [:] Defined in this module
    --------------------------
    ColorPage :: class
        Retrieve color data.

    [*] Author
     |- Gaps : sGaps : ArtGaps
"""

from os                 import path
from .MenuPage          import MenuPage , ColorIconButton
from PyQt5.QtCore       import pyqtSlot , pyqtSignal
from PyQt5.QtWidgets    import QPushButton , QWidget , QSizePolicy , QVBoxLayout
from PyQt5.QtGui        import QFont

class ColorPage( MenuPage ):
    """ Retrieve current color data from Krita """
    CDIR = path.dirname( path.abspath(__file__) )
    FG   = f"{CDIR}/images/fg.svg"
    BG   = f"{CDIR}/images/bg.svg"
    WFG  = f"{CDIR}/images/w_fg.svg"
    WBG  = f"{CDIR}/images/w_bg.svg"
    def __init__( self , backP = None , nextP = None , altP = None , parent = None ):
        super().__init__( backP    = backP  ,
                          nextP    = nextP  ,
                          parent   = parent ,
                          subTitle = "Step 2: Take color from" )
        self.color  = "FG"

        # Middle (Both Buttons)
        self.fg     = ColorIconButton( "Foreground" , True , ColorPage.FG , ColorPage.WFG , icon_size = (92,92) )
        self.bg     = ColorIconButton( "Background" , True , ColorPage.BG , ColorPage.WBG , icon_size = (92,92) )

        # Layout Setup:
        self.bottom = QWidget()
        self.bottom.setSizePolicy( QSizePolicy.Expanding , QSizePolicy.Expanding ) 
        self.sublyt = QVBoxLayout( self.bottom )
        self.sublyt.addWidget( self.fg )
        self.sublyt.addWidget( self.bg )

        self.layout.addWidget( self.bottom )

        # Connections:
        self.fg.released.connect( self.press_fg )
        self.bg.released.connect( self.press_bg )
        self.press_fg()

    @pyqtSlot()
    def press_fg( self ):
        # Visual
        self.fg.setChecked( True  )
        self.bg.setChecked( False )
        # Logical
        self.color = "FG"

    @pyqtSlot()
    def press_bg( self ):
        # Visual
        self.bg.setChecked( True )
        self.fg.setChecked( False )
        # Logical
        self.color = "BG"

    def getData( self ):
        return { "colordsc" : (self.color,None) }
