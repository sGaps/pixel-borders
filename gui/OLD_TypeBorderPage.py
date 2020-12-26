from PyQt5.QtWidgets import QWidget , QFormLayout , QPushButton , QLineEdit
from PyQt5.QtCore    import pyqtSlot , pyqtSignal
from .Page import Page

class TypeBorderPage( Page ):
    isQuickChanged = pyqtSignal( bool )
    def __init__( self , prevP = None , nextP = None , parent = None ):
        super().__init__( prevP , nextP , parent )
        # Setup Widgets:
        self.includeWidget( QPushButton("Quick")  , "quick"  )
        self.includeWidget( QPushButton("Custom") , "custom" )
        self.quick = True

        # Create connections:
        q = self.getWidget( "quick"  )
        q.setCheckable( True )

        c = self.getWidget( "custom" )
        c.setCheckable( True )

        q.released.connect( self.press_quick  )
        c.released.connect( self.press_custom )

        self.press_quick()

    @pyqtSlot()
    def press_quick( self ):
        q = self.getWidget( "quick"  )
        c = self.getWidget( "custom" )
        # Visual
        q.setChecked( True  )
        c.setChecked( False )
        # Logical
        self.quick = True
        # Signal
        self.isQuickChanged.emit( self.quick )

    @pyqtSlot()
    def press_custom( self ):
        q = self.getWidget( "quick"  )
        c = self.getWidget( "custom" )
        # Visual
        q.setChecked( False )
        c.setChecked( True  )
        # Logical
        self.quick = False
        # Signal
        self.isQuickChanged.emit( self.quick )

    def getData( self ):
        w = self.getWidget( "name" )
        return { "is-quick" : self.quick }

