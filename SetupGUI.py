from PyQt5.QtWidgets import QApplication , QVBoxLayout , QLabel
from PyQt5.QtCore    import QThread , QObject , pyqtSignal , pyqtSlot
from sys             import stderr

try:
    from krita import Krita
    KRITA_AVAILABLE = True
except:
    KRITA_AVAILABLE = False

# Graphical Interface:
from .gui.SmartMenu     import Menu
from .gui.MenuPage      import MenuPage
from .gui.NamePage      import NamePage
from .gui.TypePage      import TypePage
from .gui.ColorPage     import ColorPage
from .gui.QuickPage     import QuickPage
from .gui.CustomPage    import CustomPage
from .gui.WaitPage      import WaitPage
from .gui.TdscPage      import TdscPage
from .gui.AnimPage      import AnimPage

# Core and Built-In Modules:
from .core.Arguments    import KisData
from .core.Service      import Service , Client
from .DataLoader        import loadData , writeData
# New modules:
from .core.Border       import Border
from .core.Reader       import Reader
from .core.Generator    import Generator
from .core.KisStatus    import KisStatus
from .core.Writer       import Writer
from threading import Thread


DEBUG = True
def error_report( msg ):
    print( msg , file = stderr )

class GUI( QObject ):

    reportRequest    = pyqtSignal( str )
    errorRequest     = pyqtSignal( str )
    stepNameRequest  = pyqtSignal( str )
    stepFrameRequest = pyqtSignal( int )
    stepDoneRequest  = pyqtSignal()
    workDone     = pyqtSignal()
    rollbackDone = pyqtSignal()

    frameIncrementRequest = pyqtSignal()
    frameEraseRequest     = pyqtSignal()
    def __init__( self , title = "Pixel Borders" , parent = None ):
        super().__init__( parent )

        self.data        = {}
        self.menu        = Menu()
        self.borderizer  = None
        self.stop        = False
        self.done        = False
        self.status      = KisStatus()

        menu = self.menu
        menu.setWindowTitle( title )

        namep   = NamePage  ()
        colorp  = ColorPage ( namep   )
        typep   = TypePage  ( colorp  )
        quickp  = QuickPage ( typep   )
        customp = CustomPage( typep   )
        tdscp   = TdscPage  ( customp )
        animp   = AnimPage  ( tdscp   )
        waitp   = WaitPage  ()

        # Next Connections:
        namep.next   = colorp       # (1 -> 2)
        colorp.next  = typep        # (2 -> 3)
        typep.next , typep.altn = quickp , customp    # (3 -> 4.a | 4.b)
        quickp.next  = waitp        # (4.a -> 5)
        customp.next = tdscp        # (4.b -> 4+.b)
        tdscp.next   = animp        # (4+.b -> 4++.b)
        animp.next   = waitp        # (4++.b -> 5)

        # Krita-Dependent Code:
        animp.connect_with_krita()

        # Connections between Pages:
        typep.type_changed.connect( typep.serve_negated_alternative_request )
        typep.type_changed.connect( animp.setOverride )

        # Connections between Pages and Menu:
        namep.cancel.clicked.connect  ( menu.reject          )
        namep.info.clicked.connect    ( menu.displayInfo     )
        waitp.info.clicked.connect    ( menu.displayInfo     )
        namep.previous.clicked.connect( self.usePreviousData )

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
        # Setup simple connections here:
        waitp.accept.clicked.connect( self.menu.accept )

        # Setup progress, debug, and other report methods:
        # Visual:
        self.reportRequest.connect( waitp.usrMSG.setText )
        self.stepDoneRequest.connect( self.progressIncrement )
        # Visual & Critical:
        self.workDone.connect( waitp.raiseAccept )
        self.rollbackDone.connect( waitp.raiseAccept )
        # Visual:
        self.stepNameRequest.connect( waitp.fstep.setText )
        self.stepFrameRequest.connect( waitp.updateFrameNumber )
        # Visual & CRITICAL:
        self.rollbackDone.connect( self.onRollback )
        self.workDone.connect    ( self.onFinish )

        waitp.cancel.clicked.connect( self.sendStopRequest ) # Totally required
        menu.rejected.connect       ( self.sendStopRequest ) # as above /

        # Sub frame:
        self.frameIncrementRequest.connect( waitp.incrementFrameNumber )
        self.frameEraseRequest.connect    ( waitp.eraseFrameNumber )

    @pyqtSlot()
    def progressIncrement( self ):
        waitp = self.menu.page( "wait" )
        waitp.progress.setValue( waitp.progress.value() + 1 )

    @pyqtSlot()
    def saveConfig( self ):
        if not writeData( self.data , debug = DEBUG ):
            error_report( "[Pixel Borders]: Unable to save data." )

    @pyqtSlot()
    def usePreviousData( self ):
        self.data = loadData( debug = DEBUG )
        if self.data:
            self.menu.loadPage( "wait" )
        else:
            self.menu.page( "name" ).previous.setText( "No data to load" )

    @pyqtSlot()
    def sendStopRequest( self ):
        if self.stop or self.done: return
        self.menu.page( "wait" ).cancel.setEnabled( False )
        self.stop = True
        self.status.stopRequest()

    @pyqtSlot( bool )
    def changeMenuModal( self , modal ):
        menu = self.menu
        pos  = menu.pos()
        menu.setModal( modal )
        # Force evaluate new dialog's modal.
        # | Qt's cuteness only supports this ugly way to update Window Modal |
        menu.hide()
        menu.show()
        menu.move( pos )

    @pyqtSlot()
    def sendBorderRequest( self ):
        menu      = self.menu
        # Prevent document modification or deletion while this plugin is running.
        self.changeMenuModal( True )
        menu.raise_()

        # Disable <left| and |right> buttons
        menu.back.setEnabled( False )
        menu.next.setEnabled( False )

        # BUG: Doesn't load the previous border recipe
        cdata = self.data                       # Current Data
        pdata = menu.collectDataFromPages()     # Pages Data

        # Adds the runtime data to the last it recieved (it could be from a file)
        diff  = set( pdata.keys() ).difference( set(cdata.keys()) )
        for key in diff:
            cdata[key] = pdata[key]

        self.data = cdata.copy()
        if KRITA_AVAILABLE:
            # krita-dependent code here:
            kis  = Krita.instance()
            doc  = kis.activeDocument() if kis else None
            node = doc.activeNode()     if doc else None
            cdata["kis"]  = cdata.get( "kis"  , None ) or kis
            cdata["doc"]  = cdata.get( "doc"  , None ) or doc
            cdata["node"] = cdata.get( "node" , None ) or node

        waitp = menu.page( "wait" )
        try:
            self.arguments = KisData( cdata )
        except AttributeError as e:
            error_report( f"[Pixel Borders]: Invalid arguments: {e.args}" )
            waitp.usrMSG.setText( "Cannot run without a Krita's document.Try running \n" +
                                  "Krita in a terminal for get more information." )
            waitp.cancel.clicked.connect( menu.reject )
            waitp.cancel.setText( "Close" )
            waitp.subTitle.setText( "Unable to connect with Krita" )
            return

        if self.arguments.debug:
            self.arguments.show()

        # Visual:
        waitp.progress.reset()

        # Worker Object:
        self.borderizer = Border( kis_arguments = self.arguments,
                                  status        = self.status,
                                  setSteps      = waitp.progress.setRange,
                                  resetSteps    = waitp.progress.reset,
                                  report        = self.reportRequest.emit,      # connect with: waitp.usrMSG.setText
                                  error         = error_report,                 # report errors on stderr
                                  stepName      = self.stepNameRequest.emit,    # connect with: waitp.fstep.setText
                                  frameNumber   = self.stepFrameRequest.emit,   # connect with: waitp.updateFrameNumber
                                  frameIncrement = self.frameIncrementRequest.emit,     # connect with: waitp.incrementFrameNumber
                                  frameErase     = self.frameEraseRequest.emit,         # connect with: waitp.reset
                                  stepDone      = self.stepDoneRequest.emit,    # connect with: waitp.progress.setValue
                                  workDone      = self.workDone.emit,           # connect with: gui.onFinish, waitp.raiseAccept, .deleteLater?, thread.finished?, thread.deleteLater?
                                  rollbackDone  = self.rollbackDone.emit)       # connect with: gui.onRollback, waitp.raiseAccept)
        border          = self.borderizer

        # Worker Thread:
        self.bthread    = Thread( target = border.run )
        thread          = self.bthread

        # Run:
        thread.start()

    def onFinish( self ):
        # GUI and I/O management:
        w = self.menu.page( "wait" )
        w.subTitle.setText( "Work Done!" )
        w.fstep.hide()
        w.frame.hide()
        self.done = True
        print( "Border Done" , file = stderr )
        # Default: Animate all timeline
        del self.data['debug']
        del self.data['animation']
        del self.data['name']
        self.saveConfig()

        # Worker thread management:
        self.bthread.join()

    def onRollback( self ):
        # GUI and I/O management:
        w = self.menu.page( "wait" )
        w.fstep.hide()
        w.frame.hide()
        self.stop = True
        w.subTitle.setText( "Canceled!" )
        print( "Work Canceled" , file = stderr )

        # Worker thread management:
        self.bthread.join()

    @pyqtSlot( str )
    def reportMessage( self , msg ):
        print( f"[Borderizer]: {msg}" , file = stderr )

    @pyqtSlot()
    def run( self ):
        self.menu.show()

def main():
    platform = QApplication.instance()
    if not platform:
        platform = QApplication([])
        run      = platform.exec_
    else:
        run      = lambda: None

    gui  = GUI( "Pixel Borders - Test" )
    gui.run()
    run()

def test( _ = () ):
    main()

