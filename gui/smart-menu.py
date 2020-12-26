from PyQt5.QtCore     import Qt , pyqtSignal , pyqtSlot
from PyQt5.QtWidgets  import ( QDialog , QToolButton , QStackedWidget ,
                               QGridLayout , QSizePolicy )

# TODO: Remove
#from MenuPage import *
#from NamePage import NamePage

class Menu( QDialog ):
    def __init__( self , parent = None ):
        super().__init__( parent )

        # Menu Logic --------------
        self.pages = {}
        self.names = {}

        # Main Body ---------------
        self.layout = QGridLayout()

        # Left (Next Button) ----->
        self.next   = QToolButton()
        # Config (Next)
        szPolicy    = QSizePolicy( QSizePolicy.Preferred , QSizePolicy.Preferred )
        szPolicy.setHorizontalStretch( 0 )
        szPolicy.setVerticalStretch  ( 0 )
        szPolicy.setHeightForWidth( self.next.sizePolicy().hasHeightForWidth() )
        self.next.setSizePolicy( szPolicy )
        self.next.setCheckable( False )
        self.next.setAutoRaise( False )
        self.next.setArrowType( Qt.RightArrow )
        # TODO: Delete later
        self.next.setText( ">" )

        # Right (Back Button) <----
        self.back   = QToolButton()
        # Config (Next)
        self.back.setSizePolicy( szPolicy )
        self.back.setCheckable( False )
        self.back.setAutoRaise( False )
        self.back.setArrowType( Qt.LeftArrow )
        # TODO: Delete later
        self.back.setText( "<" )


        # Center (Page Body) -----
        self.pageBag = QStackedWidget()

        # Body (Layout) final setup:
        self.setLayout( self.layout )
        self.layout.addWidget( self.next    , 0 , 2 , 1 , 1 )
        self.layout.addWidget( self.back    , 0 , 0 , 1 , 1 )
        self.layout.addWidget( self.pageBag , 0 , 1 , 1 , 1 )

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

    def setupDefaultConnections( self ):
        self.next.released.connect( self.loadNextPage )
        self.back.released.connect( self.loadBackPage )


if __name__ == "__main__":
    from PyQt5.QtWidgets import QApplication , QVBoxLayout , QLabel
    from MenuPage  import MenuPage
    from NamePage  import NamePage
    from TypePage  import TypePage
    from ColorPage import ColorPage

    main = QApplication([])
    menu = Menu()
    menu.show()

    namep  = NamePage ()
    typep  = TypePage ( namep )
    colorp = ColorPage( typep )
    # Next Connections:
    namep.next = typep
    typep.next = colorp

    # Granular Connections:
    typep.type_changed.connect( colorp.serve_negated_alternative_request )


    # TODO: DELETE LATER. DUMMY VALUE!
    dummy1 = MenuPage( colorp )
    dummy1.layout = QVBoxLayout( dummy1 )
    dummy1.layout.addWidget(QLabel( "Option 1 <>" ))
    dummy2 = MenuPage( colorp )
    dummy2.layout = QVBoxLayout( dummy2 )
    dummy2.layout.addWidget(QLabel( "Option 2 []" ))
    colorp.next , colorp.altn = dummy1 , dummy2

    menu.addPage( namep  , "name"  )
    menu.addPage( typep  , "type"  )
    menu.addPage( colorp , "color" )

    # TODO: DELETE LATER. DUMMY VALUE!
    menu.addPage( dummy1 , "dm1" )
    menu.addPage( dummy2 , "dm2" )

    menu.setupDefaultConnections()
    main.exec_()
