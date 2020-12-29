from PyQt5.QtCore     import Qt , pyqtSignal , pyqtSlot
from PyQt5.QtWidgets  import ( QDialog , QToolButton , QStackedWidget ,
                               QMessageBox , QGridLayout , QSizePolicy )

from sys              import stderr
from threading        import Thread
from .About           import About

# Krita-dependent Code:
from .krita_connection.Lookup import KRITA_AVAILABLE , dprint
if KRITA_AVAILABLE:
    from krita import Krita

# TODO: Add custom icons for arrows!
def dirButton( text = "" , arrow_type = Qt.LeftArrow ):
    """ Returns a QToolButton with an arrow icon inside """
    bttn = QToolButton()
    szPolicy = QSizePolicy( QSizePolicy.Preferred , QSizePolicy.Preferred )
    szPolicy.setHorizontalStretch( 0 )
    szPolicy.setVerticalStretch  ( 0 )
    szPolicy.setHeightForWidth( bttn.sizePolicy().hasHeightForWidth() )

    bttn.setSizePolicy( szPolicy )
    bttn.setCheckable( False )
    bttn.setAutoRaise( True  )
    bttn.setArrowType( arrow_type )
    bttn.setText( text )
    bttn.setToolButtonStyle( Qt.ToolButtonIconOnly )
    return bttn

class Menu( QDialog ):
    def __init__( self , parent = None ):
        """ Returns a new Menu object which can be connected
            with a Borderizer object. """
        super().__init__( parent )

        # Menu Logic --------------
        self.pages  = {}            # pages as index with its names
        self.names  = {}            # page names as index
        self.sinkIX = None          # Sink Page
        self.infoON = False         # Marks when the about dialog is active
        self.infoDG = About( self ) # About dialog box.
        self.engine = None          # Future Borderizer object.
        self.worker = None          # Worker Thread (based in engine).
        self.cancel = False         # Cancel operations (and try rollback)

        # Main Body ---------------
        self.layout = QGridLayout()
        self.layout.setColumnMinimumWidth( 0 , 75  )
        self.layout.setColumnMinimumWidth( 2 , 75  )
        self.layout.setRowMinimumHeight  ( 0 , 200 )

        # Left (Next Button) ----->
        self.next   = dirButton( ">" , Qt.RightArrow )

        # Right (Back Button) <----
        self.back   = dirButton( "<" , Qt.LeftArrow  )

        # Center (Page Body) --||--
        self.pageBag = QStackedWidget()

        # Body (Layout) final setup:
        self.setLayout( self.layout )
        self.layout.addWidget( self.next    , 0 , 2 , 1 , 1 )
        self.layout.addWidget( self.back    , 0 , 0 , 1 , 1 )
        self.layout.addWidget( self.pageBag , 0 , 1 , 1 , 1 )

        # Tab Order:
        self.setTabOrder( self.next , self.back    )
        self.setTabOrder( self.back , self.pageBag )

        # Dialog Popup:
        self.infoDG.finished.connect( self.catchDisplayedInfo )

    def addPage( self , page , name ):
        """ Add a page into the Menu. the name must be unique. """
        if name not in self.pages:
            self.names[name] = page
            self.pages[page] = name
            self.pageBag.addWidget( page )

    def loadPage( self , name ):
        """ Loads a page by its name. """
        page = self.names.get( name , None )
        if page:
            self.pageBag.setCurrentWidget( page )

    @pyqtSlot()
    def loadNextPage( self ):
        """ Load the next page if there's another available. """
        if self.pages:
            page  = self.pageBag.currentWidget()
            now   = page.next
            if now and now in self.pages:
                self.pageBag.setCurrentWidget( now )

    @pyqtSlot()
    def loadBackPage( self ):
        """ Load the previous page if there's another available. """
        if self.pages:
            page  = self.pageBag.currentWidget()
            now   = page.back
            if now and now in self.pages:
                self.pageBag.setCurrentWidget( now )

    @pyqtSlot()
    def setupDefaultConnections( self ):
        """ Connect the Menu's buttons with its defaults actions. """
        self.next.released.connect( self.loadNextPage )
        self.back.released.connect( self.loadBackPage )
        self.pageBag.currentChanged.connect( self.catchPageChangeEvent )

    def collectDataFromPages( self ):
        """ return the data of all pages in the Menu as a single dict() object. """
        sum = {}
        for page in self.pages:
            sum.update( page.getData() )
        return sum

    def reportData( self , data ):
        """ Prints the data on stderr"""
        print( "[PxGUI] Data Sent: {" , file = stderr )
        for k , v in data.items():
            print( f"{' ':4}{k}: {v}" , file = stderr )
        print( "}" , file = stderr )

    @pyqtSlot( int )
    def catchPageChangeEvent( self , page_index ):
        """ Sends the border request when there's a sink page in the Menu. """
        if not self.sinkIX:           return
        if page_index != self.sinkIX: return
        self.sendBorderRequest()

    @pyqtSlot()
    def sendBorderRequest( self ):
        """ Prints the current data on stderr and sends the current
            data to an available borderizer. """
        data = self.collectDataFromPages()
        # TODO: Save the current data here (as JSON)
        # ------------------------------------------
        if KRITA_AVAILABLE and self.engine:
            # krita-dependent code here:
            kis  = Krita.instance()
            doc  = kis.activeDocument() if kis else None
            node = doc.activeNode()     if doc else None
            data["kis"]  = kis
            data["doc"]  = doc
            data["node"] = node
            self.reportData( data )

            # TODO: Move border process to a secondary thread:
            # Borderizer-dependent (engine) code here:

            # Builds a new Thread object (python 3.6+)
            # TODO: use QThreads instead the beautiful threading package...
            #       it seems QObject::startTimer cannot be used by threads else
            #       than QThreads... Nice Qt, Good one!
            #self.worker = Thread( target = self.engine.run ,
            #                      args   = ( data , )      )
            #self.worker.start()
            #self.engine.run( **data )

            # QT again...
            #self.worker = QThread()
            #self.engine.moveToThread( self.worker )


        else:
            self.reportData( data )

    @pyqtSlot()
    def usePreviousData( self ):
        """ Loads the previous data used in this Menu. Else it does nothing. """
        # TODO: Load the previous JSON. Verify if it exists. Notify if it doesn't

        # Loads the sink page:
        if self.sinkIX:
            self.pageBag.setCurrentIndex( self.sinkIX )

    @pyqtSlot( str )
    def sendRequestWhenCurrentPageIs( self , name ):
        """ Setup a page as Sink Page. When the Menu loads that page, it will
            run 'sendBorderRequest' method."""
        page = self.names.get( name , None )
        if page:
            self.sinkIX = self.pageBag.indexOf( page )


    def connectWithBorderizer( self , borderizer ):
        if self.sinkIX:
            self.engine       = borderizer
            self.engine.gui   = self
            self.engine.waitp = self.pageBag.widget( self.sinkIX )

    @pyqtSlot()
    def tryRollBack( self ):
        """ Cancel all operations when is possible """
        # TODO: Add rollback steps here:
        self.reject()

    @pyqtSlot()
    def displayInfo( self ):
        """ Show information about this plugin and its author :P """
        # Raises the children dialog box if the user press again the about button.
        if self.infoON:
            self.infoDG.raise_()
            return

        # Else, shows the dialog box
        self.infoON = True
        self.infoDG.show()

    @pyqtSlot( int )
    def catchDisplayedInfo( self , value ):
        """ Only permits display a single 'about dialog box' at time. """
        if not self.infoON: return
        self.infoON = False

    @pyqtSlot()
    def closeEvent( self , event ):
        """ Serve the close event. """
        event.accept()


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

    # Connections between Pages:
    typep.type_changed.connect( colorp.serve_negated_alternative_request )
    typep.type_changed.connect( animp.setOverride )

    # Connections between Pages and Menu:
    namep.cancel.released.connect  ( menu.reject          )
    namep.info.released.connect    ( menu.displayInfo     )
    waitp.cancel.released.connect  ( menu.tryRollBack     )
    waitp.info.released.connect    ( menu.displayInfo     )
    namep.previous.released.connect( menu.usePreviousData )

    menu.addPage( namep   , "name"   )
    menu.addPage( typep   , "type"   )
    menu.addPage( colorp  , "color"  )
    menu.addPage( quickp  , "quick"  )
    menu.addPage( customp , "custom" )
    menu.addPage( tdscp   , "transp" )
    menu.addPage( animp   , "anim"   )
    menu.addPage( waitp   , "wait"   )

    menu.setupDefaultConnections()
    menu.sendRequestWhenCurrentPageIs( "wait" )
    main.exec_()
