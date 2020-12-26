from PyQt5.QtCore       import QRect
from PyQt5.QtWidgets    import ( QWidget , QStackedWidget , QVBoxLayout , QHBoxLayout , QLayout , # Used in Menu
                                 QPushButton )              # Used in ActionButtons
from .ActionButton      import ActionButton , ICONS , TYPES

class Page( QWidget ):
    TYPE = "Normal"
    def __init__( self , prevP = None , nextP = None , parent = None ):
        super().__init__( parent )
        self.layout = QHBoxLayout()
        self.setLayout( self.layout )

        # Attributes:
        self.next = nextP
        self.prev = prevP
        self.wdgt = {}

        # Setup Buttons:
        self.Lbut = ActionButton()
        self.Rbut = ActionButton()

        # Setup Central Layout:
        self.main = QVBoxLayout()

        self.layout.addWidget( self.Lbut )
        self.layout.addLayout( self.main )
        self.layout.addWidget( self.Rbut )

        # TODO: See I really need this
        self.layout.setContentsMargins( 2 , 2 , 2 , 2 )

        self.updateL()
        self.updateR()

    def getData( self ):
        return {}

    def includeWidget( self , widget , name ):
        if name not in self.wdgt:
            self.wdgt[name] = widget
            self.main.addWidget( widget )

    def getWidget( self , name ):
        return self.wdgt.get( name , None )

    def getNext( self ):
        return self.next

    def getPrev( self ):
        return self.prev

    def setNext( self , page ):
        self.next = page
        self.updateR()

    def setPrev( self , page ):
        self.prev = page
        self.updateL()

    def updateL( self ):
        """ Updates the icon if the Lbutton """
        global TYPES , ICONS

        p = self.prev
        l = self.Lbut
        if p:
            # Get the name
            name = TYPES.get( p.typePage() , None )
            if name:
                # load the icon
                # icon = QIcon()
                # icon.loadFile( ICON[name] , ... )
                # self.Lbut.loadIcon( icon )
                pass
            else:
                # load the < icon
                # icon = QIcon()
                # icon.loadFile( ICON["<"] , ... )
                # l.loadIcon( icon )
                pass
                
            l.show()
            #Load Icon here
            pass
        else:
            l.hide()

    def updateR( self ):
        """ Updates the icon if the Rbutton """
        global TYPES , ICONS

        n = self.next
        r = self.Rbut
        if n:
            # Get the name
            name = TYPES.get( n.typePage() , None )
            if name:
                # load the icon
                # icon = QIcon()
                # icon.loadFile( ICON[name] , ... )
                # r.loadIcon( icon )
                pass
            else:
                # load the < icon
                # icon = QIcon()
                # icon.loadFile( ICON["<"] , ... )
                # r.loadIcon( icon )
                pass
                
            r.show()
            #Load Icon here
            pass
        else:
            r.hide()

    def typePage( self ):
        return Page.TYPE

# Defined to take a control of this:
class AlternativePage( Page ):
    TYPE = "Alternative"
    def __init__( self , prevP = None , nextP = None , parent = None ):
        super().__init__( prevP , nextP , parent )
        self.altP = None
        self.cond = True

    def setAlternativePage( self , page ):
        self.altP = page
        
    def swapNext( self ):
        self.altP , self.next = self.next , self.altP
        self.cond = not self.cond
        self.updateR()

    def isNormalPath( self ):
        return self.cond

    def typePage( self ):
        return AlternativePage.TYPE

# Defined to take a control of this:
class InfoPage( Page ):
    TYPE = "Info"
    def __init__( self , prevP = None , nextP = None , parent = None ):
        super().__init__( prevP , nextP , parent )

    def typePage( self ):
        return InfoPage.TYPE

class CancelPage( Page ):
    TYPE = "Cancel"
    def __init__( self , parent = None ):
        super().__init__( None , None , parent )

    def typePage( self ):
        return CancelPage.TYPE

class AcceptPage( Page ):
    TYPE = "Accept"
    def __init__( self , parent = None ):
        super().__init__( None , None , parent )

    def typePage( self ):
        return AcceptPage.TYPE
