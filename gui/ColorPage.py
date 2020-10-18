from PyQt5.QtWidgets import QWidget , QFormLayout , QPushButton , QLineEdit
from PyQt5.QtCore    import pyqtSlot , pyqtSignal

from .Page import AlternativePage

class ColorPage( AlternativePage ):
    def __init__( self , prevP = None , nextP = None , altP = None , parent = None ):
        super().__init__( prevP , nextP , parent )
        self.setAlternativePage( altP )

        self.includeWidget( QPushButton("Foreground Color") , "fg" )
        self.includeWidget( QPushButton("Background Color") , "bg" )
        self.color = "FG"

        # Create connections:
        f = self.getWidget( "fg"  )
        f.setCheckable( True )

        b = self.getWidget( "bg" )
        b.setCheckable( True )

        f.released.connect( self.press_fg )
        b.released.connect( self.press_bg )

        self.press_fg()

    @pyqtSlot( bool )
    def selectAlternative( self , change_to_quick ):
        using_quick = self.isNormalPath()
        if using_quick:
            if not change_to_quick:
                self.swapNext()
        elif change_to_quick:
            self.swapNext()

    @pyqtSlot()
    def press_fg( self ):
        f = self.getWidget( "fg"  )
        b = self.getWidget( "bg" )
        # Visual
        f.setChecked( True  )
        b.setChecked( False )
        # Logical
        self.color = "FG"

    @pyqtSlot()
    def press_bg( self ):
        f = self.getWidget( "fg"  )
        b = self.getWidget( "bg" )
        # Visual
        f.setChecked( False )
        b.setChecked( True  )
        # Logical
        self.color = "BG"

    def getData( self ):
        w = self.getWidget( "name" )
        return { "colordsc" : (self.color,None) }

