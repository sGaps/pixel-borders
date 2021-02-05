from os                 import path
from .MenuPage          import MenuPage , buttonWithIcon
from PyQt5.QtCore       import pyqtSlot , pyqtSignal
from PyQt5.QtWidgets    import QPushButton , QWidget , QSizePolicy , QVBoxLayout
from PyQt5.QtGui        import QFont

class ColorPage( MenuPage ):
    CDIR = path.dirname( path.abspath(__file__) )
    FG   = f"{CDIR}/images/fg.svg"
    BG   = f"{CDIR}/images/bg.svg"
    def __init__( self , backP = None , nextP = None , altP = None , parent = None ):
        super().__init__( backP    = backP  ,
                          nextP    = nextP  ,
                          parent   = parent ,
                          subTitle = "Step 2: Take color from" )
        self.color  = "FG"

        # Middle (Both Buttons)
        self.fg     = buttonWithIcon( "Foreground" , True , ColorPage.FG , icon_size = (92,92) )
        self.bg     = buttonWithIcon( "Background" , True , ColorPage.BG , icon_size = (92,92) )

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

    #@pyqtSlot( bool )
    #def serve_negated_alternative_request( self , to_alternative ):
    #    if (not to_alternative) != self.isAlt:
    #        self.useAlternative()

    def getData( self ):
        return { "colordsc" : (self.color,None) }
