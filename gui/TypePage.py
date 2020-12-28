from .MenuPage          import MenuPage
from PyQt5.QtCore       import pyqtSlot , pyqtSignal
from PyQt5.QtWidgets    import QPushButton
from PyQt5.QtGui        import QFont

class TypePage( MenuPage ):
    type_changed = pyqtSignal( bool )

    def __init__( self , backP = None , nextP = None , parent = None ):
        super().__init__( backP    = backP  ,
                          nextP    = nextP  ,
                          parent   = parent ,
                          subTitle = "Step 2: Which method would you like?" )
        self.is_quick = True

        font = QFont()
        font.setBold  ( True )
        font.setItalic( True )

        # Middle (Both Buttons)
        self.quick  = QPushButton( "Quick"  )
        self.quick.setFont       ( font )
        self.quick.setCheckable  ( True )
        self.custom = QPushButton( "Custom" )
        self.custom.setFont      ( font )
        self.custom.setCheckable ( True )

        # Layout Setup:
        #self.layout.addWidget( self.subTitle )
        self.layout.addWidget( self.quick    )
        self.layout.addWidget( self.custom   )

        # Connections:
        self.quick.released.connect ( self.press_quick  )
        self.custom.released.connect( self.press_custom )
        self.press_quick()

    @pyqtSlot()
    def press_quick( self ):
        # Visual
        self.quick.setChecked ( True  )
        self.custom.setChecked( False )
        # Logical
        self.is_quick = True
        self.type_changed.emit( self.is_quick )

    @pyqtSlot()
    def press_custom( self ):
        # Visual
        self.custom.setChecked( True  )
        self.quick.setChecked ( False )
        # Logical
        self.is_quick = False
        self.type_changed.emit( self.is_quick )

    def getData( self ):
        return { "is-quick" : self.is_quick }
