# Module:   gui.MenuPage.py | [ Language Python ]
# Author:   Gaps | sGaps | ArtGaps
# LICENSE:  GPLv3 (available in ./LICENSE.txt)
# ------------------------------------------------
"""
    Defines several pages for the Smart Menu.

    [:] Defined in this module
    --------------------------
    ColorIconButton :: class
        Buttons with icons that works on Light and Dark themes.

    subTitleLabel :: function
        makes custom QLabels

    MenuPage :: class
        Simple Page of a menu wizard.

    AlternativePage :: class
        Page with 3 possible paths.

    SinkPage :: class
        Page without any possible paths.

    [*] Author
     |- Gaps : sGaps : ArtGaps
"""

from PyQt5.QtCore     import Qt , QEvent , pyqtSignal , pyqtSlot , QSize
from PyQt5.QtWidgets  import QWidget , QLabel , QToolButton , QVBoxLayout , QSizePolicy
from PyQt5.QtGui      import QFont , QIcon , QPalette

DEFAULT_PAGE_SIZE = (400 , 300)

DEFAULT_FONT      = QFont()
DEFAULT_FONT.setFamily( u"Cantarell" )
DEFAULT_FONT.setBold  ( True )
DEFAULT_FONT.setItalic( True )
DEFAULT_FONT.setWeight(  75  )

TextUnderIcon  = Qt.ToolButtonStyle.ToolButtonTextUnderIcon
TextBesideIcon = Qt.ToolButtonStyle.ToolButtonTextBesideIcon

class ColorIconButton( QToolButton ):
    """ Custom Class to have icons with light/dark themes. """
    def __init__( self , text = "" ,
                         checkable = True,
                         icon_light = "" ,
                         icon_dark = "" ,
                         icon_pos = TextBesideIcon,
                         icon_size = (48,48) , # Can be null
                         font = None ,
                         sizePolicy = None,
                         parent = None ):
        super().__init__(parent)
        self.setText(text)
        self.setCheckable( checkable )
        self.setToolButtonStyle( icon_pos )

        szPolicy = sizePolicy or QSizePolicy( QSizePolicy.Preferred , QSizePolicy.Preferred ) 
        self.setSizePolicy( szPolicy )

        if font:
            button.setFont( font )
        self.icon_light = QIcon(icon_light or "" )
        self.icon_dark  = QIcon(icon_dark  or "" )
        if icon_size:
            self.icon_size  = QSize(*icon_size)
            self.setIconSize( self.icon_size )
        # Force initial update:
        self.changeEvent( QEvent(QEvent.PaletteChange) )

    def backgroundColor( self ):
        return self.palette().color( QPalette.Background )

    def textColor( self ):
        return self.palette().color( QPalette.Text )

    def changeEvent( self , event ):
        palette = None
        etype   = event.type()
        if etype == QEvent.ApplicationPaletteChange:
            palette = QApplication.instance().palette()
        elif etype == QEvent.PaletteChange:
            palette = self.palette()

        if palette:
            if ColorIconButton.tooLight( palette ):
                self.setIcon( self.icon_light )
            else:
                self.setIcon( self.icon_dark )
        super().changeEvent( event )

    @staticmethod
    def tooLight( palette ):
        bg = palette.color( QPalette.Background )
        return bg.lightness() > 110 # [0..100] is too dark. [120..255] is too light.

def subTitleLabel( text , font = DEFAULT_FONT ):
    """ Returns a bold text that can be used as a sub title """
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

