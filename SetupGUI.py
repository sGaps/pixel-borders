from PyQt5.QtWidgets import QApplication , QVBoxLayout , QLabel
from PyQt5.QtCore    import QThread , QObject , pyqtSignal , pyqtSlot
from sys             import stderr

try:
    from krita import Krita
    KRITA_AVAILABLE = True
except:
    KRITA_AVAILABLE = False

# TODO: Clean this sequence
from importlib import reload

try:
    # Krita has some problems with module paths (why? idk)
    import pixel_borders.gui.SmartMenu  as SM
    import pixel_borders.gui.MenuPage   as MP
    import pixel_borders.gui.NamePage   as NP
    import pixel_borders.gui.TypePage   as YP
    import pixel_borders.gui.ColorPage  as KP
    import pixel_borders.gui.QuickPage  as QP
    import pixel_borders.gui.CustomPage as CP
    import pixel_borders.gui.WaitPage   as WP
    import pixel_borders.gui.TdscPage   as TP
    import pixel_borders.gui.AnimPage   as AP
    import pixel_borders.core.Borderizer as BD
    import pixel_borders.core.Arguments  as AR
    import pixel_borders.core.Service    as SV
    outsideKRITA = False
except:
    import gui.SmartMenu  as SM
    import gui.MenuPage   as MP
    import gui.NamePage   as NP
    import gui.TypePage   as YP
    import gui.ColorPage  as KP
    import gui.QuickPage  as QP
    import gui.CustomPage as CP
    import gui.WaitPage   as WP
    import gui.TdscPage   as TP
    import gui.AnimPage   as AP
    import core.Borderizer as BD
    import core.Arguments  as AR
    import core.Service    as SV
    outsideKRITA = True

# TODO: Delete later
# NOTE: I'm able to use this with
reload( SM )
reload( MP )
reload( NP )
reload( YP )
reload( KP )
reload( QP )
reload( CP )
reload( WP )
reload( TP )
reload( AP )
reload( BD )
reload( AR )
reload( SV )

Menu       = SM.Menu
MenuPage   = MP.MenuPage
NamePage   = NP.NamePage
TypePage   = YP.TypePage
ColorPage  = KP.ColorPage
QuickPage  = QP.QuickPage
CustomPage = CP.CustomPage
WaitPage   = WP.WaitPage
TdscPage   = TP.TdscPage
AnimPage   = AP.AnimPage
Borderizer = BD.Borderizer
KisData    = AR.KisData
Service    = SV.Service
Client     = SV.Client

if outsideKRITA:
    main = QApplication([])

class GUI( QObject ):
    userCanceled = pyqtSignal( str )
    def __init__( self , title = "Pixel Borders" , parent = None ):
        super().__init__( parent )

        self.data        = {}
        self.menu        = Menu()
        self.borderizer  = None
        self.stop        = False
        self.done        = False

        menu = self.menu
        menu.setWindowTitle( title )

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

        # Krita-Dependent Code:
        animp.connect_with_krita()

        # Connections between Pages:
        typep.type_changed.connect( colorp.serve_negated_alternative_request )
        typep.type_changed.connect( animp.setOverride )

        # Connections between Pages and Menu:
        namep.cancel.released.connect  ( menu.reject          )
        namep.info.released.connect    ( menu.displayInfo     )
        waitp.info.released.connect    ( menu.displayInfo     )
        namep.previous.released.connect( self.usePreviousData )

        menu.addPage( namep   , "name"   )
        menu.addPage( typep   , "type"   )
        menu.addPage( colorp  , "color"  )
        menu.addPage( quickp  , "quick"  )
        menu.addPage( customp , "custom" )
        menu.addPage( tdscp   , "transp" )
        menu.addPage( animp   , "anim"   )
        menu.addPage( waitp   , "wait"   )

        menu.setupDefaultConnections()
        menu.notifyForSinkPage( "wait" )

        menu.isOnSinkPage.connect( self.sendBorderRequest )
        menu.isOnSinkPage.connect( waitp.raiseCancel     )
        # Setup thread connections here:
        waitp.accept.released.connect( self.menu.accept )

    @pyqtSlot()
    def saveConfig( self ):
        pass

    @pyqtSlot()
    def usePreviousData( self ):
        # TODO: Loads the data as JSON
        self.data = {}
        self.menu.loadPage( "wait" )

    @pyqtSlot()
    def sendStopRequest( self ):
        if self.stop or self.done: return
        self.stop = True
        self.borderizer.stopRequest()

    @pyqtSlot()
    def sendBorderRequest( self ):
        menu      = self.menu
        self.data = self.data if self.data else menu.collectDataFromPages()
        cdata     = self.data.copy()
        if KRITA_AVAILABLE:
            # krita-dependent code here:
            kis  = Krita.instance()
            doc  = kis.activeDocument() if kis else None
            node = doc.activeNode()     if doc else None
            cdata["kis"]  = kis
            cdata["doc"]  = doc
            cdata["node"] = node

        waitp = menu.page( "wait" )
        try:
            self.arguments = KisData( cdata )
        except AttributeError as e:
            print( f"[Pixel Borders Extension] Invalid arguments: {e.args}" )
            waitp.dbgMSG.setText( "Cannot run without a Krita's document.Try running \n" +
                                  "Krita in a terminal for get more information." )
            waitp.cancel.released.connect( menu.reject )
            return
        waitp.progress.setRange( self.arguments.start , self.arguments.finish )
        waitp.progress.reset()

        self.borderizer = Borderizer( self.arguments )
        border          = self.borderizer

        # Setup Connections:
        border.debug.connect( waitp.dbgMSG.setText )

        # Visual:
        border.progress.connect( waitp.progress.setValue )
        border.workDone.connect( waitp.raiseAccept       )

        # Cancel:
        waitp.cancel.released.connect ( self.sendStopRequest ) # Execute the shared code in the main thread
        menu.rejected.connect         ( self.sendStopRequest ) # as above /
        border.rollbackRequest.connect( border.rollback      )
        border.rollbackDone.connect   ( self.onRollback      )
        border.rollbackDone.connect   ( waitp.raiseAccept    )

        # Finishing all:
        border.workDone.connect( self.onFinish      ) # NOTE: (finished -> thread execution end) != (workDone -> task done successfully )
        border.finished.connect( border.quit        )
        border.finished.connect( border.deleteLater )

        # Run:
        border.start()

    def onFinish( self ):
        self.done = True
        print( "Border Done" )
        self.saveConfig()

    def onRollback( self ):
        print( "Work Canceled" )

    @pyqtSlot( str )
    def reportMessage( self , msg ):
        print( f"[Borderizer]: {msg}" )

    @pyqtSlot()
    def run( self ):
        self.menu.show()

        if outsideKRITA:
            main.exec_()

# NOTE: I had some issues trying to run the kritarunner of Krita 4.4.x. It seems that it requires
#       a function with type (f :: a -> () ). So, I use for test this safely...
#       >>>     $ kritarunner -s SetupGUI -f test
def test( _ ):
    gui = GUI( "Pixel Borders - Test" )
    gui.run()

if __name__ == "__main__":
    gui = GUI( "Pixel Borders - Test" )
    gui.run()
