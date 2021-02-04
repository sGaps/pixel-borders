from os                 import path
from .MenuPage          import MenuPage , buttonWithIcon , TextBesideIcon
from PyQt5.QtCore       import pyqtSlot , pyqtSignal , Qt
from PyQt5.QtWidgets    import QPushButton , QToolButton , QWidget , QVBoxLayout , QSizePolicy
from PyQt5.QtGui        import QFont , QIcon

class TypePage( MenuPage ):
    CDIR         = path.dirname( path.abspath(__file__) )
    CUSTOM       = f"{CDIR}/images/custom.svg"
    QUICK        = f"{CDIR}/images/quick.svg"
    type_changed = pyqtSignal( bool )

    def __init__( self , backP = None , nextP = None , parent = None ):
        super().__init__( backP    = backP  ,
                          nextP    = nextP  ,
                          parent   = parent ,
                          subTitle = "Step 2: Which method would you like?" )
        self.is_quick = True

        #font = QFont()
        #font.setBold  ( True )
        #font.setItalic( True )

        # Middle (Both Buttons)
        self.quick  = buttonWithIcon( "Quick"   , True , TypePage.QUICK  , icon_size = (92,92) )
        self.custom = buttonWithIcon( "Custom " , True , TypePage.CUSTOM , icon_size = (92,92) )
        #self.quick  = QToolButton()
        #self.quick.setText( "Quick" )
        #self.quick.setFont       ( font )
        #self.quick.setCheckable  ( True )
        #self.quick.setIcon( QIcon(TypePage.QUICK) )
        #self.quick.setToolButtonStyle( Qt.ToolButtonStyle.ToolButtonTextUnderIcon )
        #self.quick.setSizePolicy( QSizePolicy.Preferred , QSizePolicy.Preferred )

        #self.custom = QToolButton()
        #self.custom.setText( "Custom" )
        #self.custom.setFont      ( font )
        #self.custom.setCheckable ( True )
        #self.custom.setIcon( QIcon(TypePage.CUSTOM) )
        #self.custom.setToolButtonStyle( Qt.ToolButtonStyle.ToolButtonTextUnderIcon )
        #self.custom.setSizePolicy( QSizePolicy.Preferred , QSizePolicy.Preferred )

        self.bottom = QWidget()
        self.bottom.setSizePolicy( QSizePolicy.Expanding , QSizePolicy.Expanding ) 
        self.sublyt = QVBoxLayout( self.bottom )
        self.sublyt.addWidget( self.quick  )
        self.sublyt.addWidget( self.custom )

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

    def getData( self ):
        return { "is-quick" : self.is_quick }
