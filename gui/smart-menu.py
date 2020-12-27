from PyQt5.QtCore     import Qt , pyqtSignal , pyqtSlot
from PyQt5.QtWidgets  import ( QDialog , QToolButton , QStackedWidget ,
                               QGridLayout , QSizePolicy )

from sys              import stderr
from krita_connection.Lookup import KRITA_AVAILABLE , dprint
if KRITA_AVAILABLE:
    from krita import Krita

def dirButton( text = "" , arrow_type = Qt.LeftArrow ):
        bttn = QToolButton()
        szPolicy = QSizePolicy( QSizePolicy.Preferred , QSizePolicy.Preferred )
        szPolicy.setHorizontalStretch( 0 )
        szPolicy.setVerticalStretch  ( 0 )
        szPolicy.setHeightForWidth( bttn.sizePolicy().hasHeightForWidth() )

        bttn.setSizePolicy( szPolicy )
        bttn.setCheckable( False )
        bttn.setAutoRaise( False )
        bttn.setArrowType( arrow_type )
        bttn.setText( text )
        return bttn

class Menu( QDialog ):
    def __init__( self , parent = None ):
        super().__init__( parent )

        # Menu Logic --------------
        self.pages = {}
        self.names = {}

        # Main Body ---------------
        self.layout = QGridLayout()
        self.layout.setColumnMinimumWidth( 0 , 75  )
        self.layout.setColumnMinimumWidth( 2 , 75  )
        self.layout.setRowMinimumHeight  ( 0 , 200 )

        # Left (Next Button) ----->
        self.next   = dirButton( ">" , Qt.LeftArrow )

        # Right (Back Button) <----
        self.back   = dirButton( "<" , Qt.LeftArrow )

        # Center (Page Body) -----
        self.pageBag = QStackedWidget()

        # Body (Layout) final setup:
        self.setLayout( self.layout )
        self.layout.addWidget( self.next    , 0 , 2 , 1 , 1 )
        self.layout.addWidget( self.back    , 0 , 0 , 1 , 1 )
        self.layout.addWidget( self.pageBag , 0 , 1 , 1 , 1 )

        # Tab Order:
        self.setTabOrder( self.next , self.back    )
        self.setTabOrder( self.back , self.pageBag )

    def addPage( self , page , name ):
        if name not in self.pages:
            self.names[name] = page
            self.pages[page] = name
            self.pageBag.addWidget( page )

    def loadPage( self , name ):
        page = self.name.get( name , None )
        if page:
            self.pageBag.setCurrentWidget( page )

    @pyqtSlot()
    def loadNextPage( self ):
        if self.pages:
            page  = self.pageBag.currentWidget()
            now   = page.next
            if now and now in self.pages:
                self.pageBag.setCurrentWidget( now )

    @pyqtSlot()
    def loadBackPage( self ):
        if self.pages:
            page  = self.pageBag.currentWidget()
            now   = page.back
            if now and now in self.pages:
                self.pageBag.setCurrentWidget( now )

    @pyqtSlot()
    def setupDefaultConnections( self ):
        self.next.released.connect( self.loadNextPage )
        self.back.released.connect( self.loadBackPage )

    def collectDataFromPages( self ):
        sum = {}
        for page in self.pages:
            sum.update( page.getData() )
        return sum

    def reportData( self , data ):
        print( "[PxGUI] Data Sent: {" , file = stderr )
        for k , v in data.items():
            print( f"{' ':4}{k}: {v}" , file = stderr )
        print( "}" , file = stderr )

    @pyqtSlot()
    def sendBorderRequest( self ):
        data = self.collectDataFromPages()
        if KRITA_AVAILABLE:
            # Add krita-dependent information here:
            kis  = Krita.instance()
            doc  = kis.activeDocument()
            node = doc.activeNode()
            data["kis"]  = kis
            data["doc"]  = doc
            data["node"] = node
            self.reportData( data )
            # TODO: Add calculation here in a secondary thread:
        else:
            self.reportData( data )

if __name__ == "__main__":
    from PyQt5.QtWidgets import QApplication , QVBoxLayout , QLabel
    from MenuPage   import MenuPage
    from NamePage   import NamePage
    from TypePage   import TypePage
    from ColorPage  import ColorPage
    from QuickPage  import QuickPage
    from CustomPage import CustomPage
    from WaitPage   import WaitPage
    from TdscPage   import TdscPage
    from AnimPage   import AnimPage

    main = QApplication([])
    menu = Menu()
    menu.show()

    namep   = NamePage  ()
    typep   = TypePage  ( namep   )
    colorp  = ColorPage ( typep   )
    quickp  = QuickPage ( colorp  )
    customp = CustomPage( colorp  )
    tdscp   = TdscPage  ( customp )
    animp   = AnimPage  ( tdscp   )
    waitp   = WaitPage  ()
    # Next Connections:
    namep.next   = typep      # (1 -> 2)
    typep.next   = colorp     # (2 -> 3)
    colorp.next , colorp.altn = quickp , customp    # (3 -> 4.a | 4.b)
    quickp.next  = waitp
    customp.next = tdscp
    tdscp.next   = animp
    animp.next   = waitp

    # Granular Connections:
    typep.type_changed.connect( colorp.serve_negated_alternative_request )
    typep.type_changed.connect( animp.setOverride )

    menu.addPage( namep   , "name"   )
    menu.addPage( typep   , "type"   )
    menu.addPage( colorp  , "color"  )
    menu.addPage( quickp  , "quick"  )
    menu.addPage( customp , "custom" )
    menu.addPage( tdscp   , "transp" )
    menu.addPage( animp   , "anim"   )
    menu.addPage( waitp   , "wait"   )

    menu.setupDefaultConnections()
    main.exec_()
    menu.sendBorderRequest()
