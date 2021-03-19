from os                 import path
from .MenuPage          import AlternativePage , ColorIconButton , TextBesideIcon
from PyQt5.QtCore       import pyqtSlot , pyqtSignal , Qt
from PyQt5.QtWidgets    import QPushButton , QToolButton , QWidget , QVBoxLayout , QSizePolicy
from PyQt5.QtGui        import QFont , QIcon

class TypePage( AlternativePage ):
    CDIR         = path.dirname( path.abspath(__file__) )
    CUSTOM       = f"{CDIR}/images/custom.svg"
    QUICK        = f"{CDIR}/images/quick.svg"

    WCUSTOM      = f"{CDIR}/images/w_custom.svg"
    WQUICK       = f"{CDIR}/images/w_quick.svg"
    type_changed = pyqtSignal( bool )

    def __init__( self , backP = None , nextP = None , parent = None ):
        super().__init__( backP    = backP  ,
                          nextP    = nextP  ,
                          parent   = parent ,
                          subTitle = "Step 3: Which method would you like?" )
        # Toggle
        self.is_quick = True

        # Middle (Both Buttons)
        self.quick  = ColorIconButton( "Quick"   , True , TypePage.QUICK  , TypePage.WQUICK  , icon_size = (92,92) )
        self.custom = ColorIconButton( "Custom " , True , TypePage.CUSTOM , TypePage.WCUSTOM , icon_size = (92,92) )

        self.bottom = QWidget()
        self.bottom.setSizePolicy( QSizePolicy.Expanding , QSizePolicy.Expanding ) 
        self.sublyt = QVBoxLayout( self.bottom )
        self.sublyt.addWidget( self.custom )
        self.sublyt.addWidget( self.quick  )

        # Layout Setup:
        self.layout.addWidget( self.bottom )

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

    @pyqtSlot( bool )
    def serve_negated_alternative_request( self , to_alternative ):
        if (not to_alternative) != self.isAlt:
            self.useAlternative()

    def getData( self ):
        return { "is-quick" : self.is_quick }
