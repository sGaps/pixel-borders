from PyQt5.QtCore     import Qt , pyqtSignal , pyqtSlot
from PyQt5.QtWidgets  import QWidget , QLabel
from PyQt5.QtGui      import QFont

DEFAULT_PAGE_SIZE = (400 , 200)

DEFAULT_FONT      = QFont()
DEFAULT_FONT.setFamily( u"Cantarell" )
DEFAULT_FONT.setBold  ( True )
DEFAULT_FONT.setItalic( True )
DEFAULT_FONT.setWeight(  75  )

def subTitleLabel( text , font = DEFAULT_FONT ):
    label = QLabel( text )
    label.setFont( font )
    label.setAlignment( Qt.AlignCenter )
    return label

class MenuPage( QWidget ):
    """
        A MenuPage can go to left or right:
        [ backP ] <-- [ MenuPage ] --> [ nextP ]
    """
    def __init__( self , backP = None , nextP = None , altNextP = None , parent = None ):
        super().__init__( parent )
        self.resize( *DEFAULT_PAGE_SIZE )

        self.next   = nextP
        self.back   = backP
        # It requires a manual layout setup
        self.layout = None

    def getData( self ):
        return {}


class AlternativePage( MenuPage ):
    """
        An AlternativePage can go to left, right or even, it can go to
        another page (the reason why it's called alternative)
        [ backP ] <-- [ MenuPage ] --> [ nextP ]
                          |
                          |- - - - --> [ altNextP ]
    """
    def __init__( self , backP = None , nextP = None , altNextP = None , parent = None ):
        super().__init__( backP , nextP , parent )
        self.altn  = altNextP
        self.isAlt = False

    @pyqtSlot()
    def useAlternative( self ):
        if self.altn:
            self.altn , self.next = self.next , self.altn
            self.isAlt = not self.isAlt

class SinkPage( MenuPage ):
    """
        A sink Page cannot go to another page.
        _- [ MenuPage ] -_
    """
    def __init__( self , parent = None ):
        super().__init__( None , None , parent )