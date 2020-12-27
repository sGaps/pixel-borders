from MenuPage           import AlternativePage
from PyQt5.QtCore       import pyqtSlot , pyqtSignal
from PyQt5.QtWidgets    import QPushButton
from PyQt5.QtGui        import QFont

class ColorPage( AlternativePage ):
    def __init__( self , backP = None , nextP = None , altP = None , parent = None ):
        super().__init__( backP    = backP  ,
                          nextP    = nextP  ,
                          parent   = parent ,
                          subTitle = "Step 3: Take color from" )
        self.color  = "FG"

        font = QFont()
        font.setBold  ( True )
        font.setItalic( True )

        # Middle (Both Buttons)
        self.fg = QPushButton( "Foreground" )
        self.fg.setFont      ( font )
        self.fg.setCheckable ( True )
        self.bg = QPushButton( "Background" )
        self.bg.setFont      ( font )
        self.bg.setCheckable ( True )

        # Layout Setup:
        self.layout.addWidget( self.fg       )
        self.layout.addWidget( self.bg       )

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

    @pyqtSlot( bool )
    def serve_negated_alternative_request( self , to_alternative ):
        if (not to_alternative) != self.isAlt:
            self.useAlternative()

    def getData( self ):
        return { "colordsc" : (self.color,None) }
