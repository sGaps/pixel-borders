from PyQt5.QtCore     import Qt , pyqtSignal , pyqtSlot , QSize
from PyQt5.QtWidgets  import QWidget , QLabel , QToolButton , QVBoxLayout , QSizePolicy
from PyQt5.QtGui      import QFont , QIcon

DEFAULT_PAGE_SIZE = (400 , 300)

DEFAULT_FONT      = QFont()
DEFAULT_FONT.setFamily( u"Cantarell" )
DEFAULT_FONT.setBold  ( True )
DEFAULT_FONT.setItalic( True )
DEFAULT_FONT.setWeight(  75  )

TextUnderIcon  = Qt.ToolButtonStyle.ToolButtonTextUnderIcon
TextBesideIcon = Qt.ToolButtonStyle.ToolButtonTextBesideIcon

def buttonWithIcon( text = "option"     , checkable = False , icon_path = "" ,
                    icon_pos  = TextBesideIcon , icon_size = (48,48) , font = DEFAULT_FONT ):
    button = QToolButton()
    button.setText( text )
    button.setCheckable( checkable )
    button.setToolButtonStyle( icon_pos )
    button.setSizePolicy( QSizePolicy.Preferred , QSizePolicy.Preferred )
    if font:      button.setFont( font )
    if icon_path:
        button.setIcon( QIcon(icon_path) )
        if icon_size: button.setIconSize( QSize(*icon_size) )
    return button

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
    def __init__( self , backP = None , nextP = None ,
                  parent = None , subTitle = "" ):
        super().__init__( parent )
        self.resize( *DEFAULT_PAGE_SIZE )

        self.next   = nextP
        self.back   = backP
        # It requires a manual layout setup
        self.layout   = QVBoxLayout  ( self )
        self.subTitle = subTitleLabel( subTitle )
        self.layout.addWidget( self.subTitle , 0 , Qt.AlignCenter |
                                                   Qt.AlignTop    )
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
    def __init__( self , backP = None , nextP = None ,
                  altNextP = None , parent = None , subTitle = "" ):
        super().__init__( backP    = backP    ,
                          nextP    = nextP    ,
                          parent   = parent   ,
                          subTitle = subTitle )
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
    def __init__( self , parent = None , subTitle = "" ):
        super().__init__( backP    = None     ,
                          nextP    = None     ,
                          parent   = parent   ,
                          subTitle = subTitle )
