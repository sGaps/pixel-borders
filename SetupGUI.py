from PyQt5.QtWidgets import QApplication , QVBoxLayout , QLabel
from PyQt5.QtCore    import QThread , QObject , pyqtSignal , pyqtSlot
from sys             import stderr

try:
    from krita import Krita
    KRITA_AVAILABLE = True
except:
    KRITA_AVAILABLE = False

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
from .core.Borderizer   import Borderizer
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

class GUI( QObject ):
    userCanceled = pyqtSignal( str ) # TODO: Verify if this can be deleted.

    reportRequest    = pyqtSignal( str )
    errorRequest     = pyqtSignal( str )
    stepNameRequest  = pyqtSignal( str )
    stepFrameRequest = pyqtSignal( int )
    progressRequest  = pyqtSignal( int ) # TODO: DELETE? MAYBE IT'S USELESS
    stepDoneRequest  = pyqtSignal()
    workDone     = pyqtSignal()
    rollbackDone = pyqtSignal()

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

        #self.errorRequest.connect( self.reportMessage )
        waitp.cancel.clicked.connect( self.sendStopRequest ) # Totally required
        menu.rejected.connect       ( self.sendStopRequest ) # as above /

    @pyqtSlot()
    def progressIncrement( self ):
        waitp = self.menu.page( "wait" )
        waitp.progress.setValue( waitp.progress.value() + 1 )

    @pyqtSlot()
    def saveConfig( self ):
        # TODO: Notify when something goes wrong
        writeData( self.data , debug = DEBUG )

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
        print( f"Pressed sendStopRequest by someone" )
        self.menu.page( "wait" ).cancel.setEnabled( False )
        self.stop = True
        self.status.stopRequest()
        #self.borderizer.stopRequest()

    @pyqtSlot( bool )
    def changeMenuModal( self , modal ):
        menu = self.menu
        pos  = menu.pos()
        menu.setModal( modal )
        # Force evaluate new dialog's modal.
        # | Qt's cuteness only supports this ugly way for update Window Modalities |
        menu.hide()
        menu.show()
        menu.move( pos )

    @pyqtSlot()
    def ___________sendBorderRequest________OLD( self ):
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
            print( f"[Pixel Borders Extension] Invalid arguments: {e.args}" , file = stderr )
            waitp.usrMSG.setText( "Cannot run without a Krita's document.Try running \n" +
                                  "Krita in a terminal for get more information." )
            waitp.cancel.clicked.connect( menu.reject )
            waitp.cancel.setText( "Close" )
            waitp.subTitle.setText( "Unable to connect with Krita" )
            return

        if self.arguments.debug:
            self.arguments.show()

        # Visual:
        waitp.progress.setRange( self.arguments.start , self.arguments.finish )
        waitp.progress.reset()

        # Worker Thread:
        self.bthread     = QThread()
        self.borderizer = Borderizer( self.arguments , cleanUpAtFinish = True )
        border          = self.borderizer
        thread          = self.bthread

        # Concurrency:
        border.moveToThread( thread )
        thread.started.connect( border.run )
        thread.setObjectName( "Borderizer-Thread" )

        # Setup Connections:
        border.report.connect( waitp.usrMSG.setText )

        # Visual:
        border.progress.connect( waitp.progress.setValue )
        border.workDone.connect( waitp.raiseAccept       )
        # Visual (sub progress)
        border.stepName.connect   ( waitp.fstep.setText     )
        border.frameNumber.connect( waitp.updateFrameNumber )

        # Cancel:
        waitp.cancel.clicked.connect  ( self.sendStopRequest ) # Execute the shared code in the main thread
        menu.rejected.connect         ( self.sendStopRequest ) # as above /
        border.rollbackRequest.connect( border.rollback      )
        border.rollbackDone.connect   ( waitp.raiseAccept    )

        # Finishing all:
        # NOTE: (finished -> thread execution end) != (workDone -> task done successfully)
        border.workDone.connect( self.onFinish      )
        border.workDone.connect( thread.quit        ) # Tells to the thread it can be deleted.
        border.rollbackDone.connect( thread.quit    ) # Tells to the thread it can be deleted. 
        thread.finished.connect( border.deleteLater )
        thread.finished.connect( thread.deleteLater )

        #<<<# Tasks to do when finished normally or with errors
        #<<<border.workDone.connect    ( self.onFinish   )
        #<<<border.rollbackDone.connect( self.onRollback )

        #<<<# Cleanup action [Quit the thread] -> tells to the Worker Thread it can be deleted
        #<<<border.workDone.connect    ( thread.quit    )
        #<<<border.rollbackDone.connect( thread.quit    )

        #<<<#thread.finished.connect( border.deleteLater )
        #<<<# Cleanup actions [Border (done by itself), Thread (done by GUI)]
        #<<<border.workDone.connect    ( border.deleteLater )
        #<<<border.rollbackDone.connect( border.deleteLater )
        #<<<#thread.finished.connect    ( thread.deleteLater )

        print( f"Service's Thread: {self.arguments.service.thread()} before start" )
        # Run:
        thread.start()
        # WARNING ^^^ OLD VERSION THERE ^^^

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
            print( f"[Pixel Borders Extension] Invalid arguments: {e.args}" , file = stderr )
            waitp.usrMSG.setText( "Cannot run without a Krita's document.Try running \n" +
                                  "Krita in a terminal for get more information." )
            waitp.cancel.clicked.connect( menu.reject )
            waitp.cancel.setText( "Close" )
            waitp.subTitle.setText( "Unable to connect with Krita" )
            return

        if self.arguments.debug:
            self.arguments.show()

        # Visual:
        #waitp.progress.setRange( self.arguments.start , self.arguments.finish )
        waitp.progress.reset()

        # Worker Object:
        self.borderizer = Border( kis_arguments = self.arguments,
                                  status        = self.status,
                                  setSteps      = waitp.progress.setRange,
                                  resetSteps    = waitp.progress.reset,
                                  report        = self.reportRequest.emit,      # connect with: waitp.usrMSG.setText
                                  #error         = self.errorRequest.emit,       # connect with: console print
                                  error         = print,       # connect with: console print
                                  stepName      = self.stepNameRequest.emit,    # connect with: waitp.fstep.setText
                                  frameNumber   = self.stepFrameRequest.emit,   # connect with: waitp.updateFrameNumber
                                  #progress      = self.progressRequest.emit,    # connect with: waitp.progress.setValue
                                  stepDone      = self.stepDoneRequest.emit,    # connect with: waitp.progress.setValue
                                  workDone      = self.workDone.emit,           # connect with: gui.onFinish, waitp.raiseAccept, .deleteLater?, thread.finished?, thread.deleteLater?
                                  rollbackDone  = self.rollbackDone.emit)       # connect with: gui.onRollback, waitp.raiseAccept)
        border          = self.borderizer

        # Worker Thread:
        self.bthread    = Thread( target = border.run )
        thread          = self.bthread

        # Concurrency:
        #thread.started.connect( border.run )
        #thread.setObjectName( "Borderizer-Thread" )

        # Setup Connections:
        #border.report.connect( waitp.usrMSG.setText )

        # Visual:
        ##border.progress.connect( waitp.progress.setValue )
        ##border.workDone.connect( waitp.raiseAccept       )
        # Visual (sub progress)
        ##border.stepName.connect   ( waitp.fstep.setText     )
        ##border.frameNumber.connect( waitp.updateFrameNumber )

        # Cancel:
        #waitp.cancel.clicked.connect  ( self.sendStopRequest ) # Totally required
        #menu.rejected.connect         ( self.sendStopRequest ) # as above /
        ##border.rollbackRequest.connect( border.rollback      )
        ##border.rollbackDone.connect   ( waitp.raiseAccept    )

        # Finishing all:
        # NOTE: (finished -> thread execution end) != (workDone -> task done successfully)
        #border.workDone.connect( self.onFinish      )
        #border.workDone.connect( thread.quit        ) # Tells to the thread it can be deleted.
        #border.rollbackDone.connect( thread.quit    ) # Tells to the thread it can be deleted. 
        #thread.finished.connect( border.deleteLater )
        #thread.finished.connect( thread.deleteLater )

        #<<<# Tasks to do when finished normally or with errors
        #<<<border.workDone.connect    ( self.onFinish   )
        #<<<border.rollbackDone.connect( self.onRollback )

        #<<<# Cleanup action [Quit the thread] -> tells to the Worker Thread it can be deleted
        #<<<border.workDone.connect    ( thread.quit    )
        #<<<border.rollbackDone.connect( thread.quit    )

        #<<<#thread.finished.connect( border.deleteLater )
        #<<<# Cleanup actions [Border (done by itself), Thread (done by GUI)]
        #<<<border.workDone.connect    ( border.deleteLater )
        #<<<border.rollbackDone.connect( border.deleteLater )
        #<<<#thread.finished.connect    ( thread.deleteLater )

        print( f"Service's Thread: {self.arguments.service.thread()} before start" )
        # Run:
        thread.start()

    def onFinish( self ):
        # Worker thread management:
        #thread = self.bthread
        #thread.quit()
        #thread.wait()
        #thread.deleteLater()


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
        #print(  f"Thread's Value:       {self.bthread}\n" +
        #        f"         is running?  {self.bthread.isRunning()}\n" +
        #        f"         is finished? {self.bthread.isFinished()}\n" )
        self.bthread.join()

    def onRollback( self ):
        # Worker thread management:
        #thread = self.bthread
        #thread.quit()
        #thread.wait()
        #thread.deleteLater()

        # GUI and I/O management:
        w = self.menu.page( "wait" )
        w.fstep.hide()
        w.frame.hide()
        self.stop = True
        w.subTitle.setText( "Canceled!" )
        print( "Work Canceled" , file = stderr )
        #print(  f"Thread's Value:       {self.bthread}\n" +
        #        f"         is running?  {self.bthread.isRunning()}\n" +
        #        f"         is finished? {self.bthread.isFinished()}\n" )
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
    """ Run QuickMode """
    # Prelude ------------------------
    platform = QApplication.instance()
    if not platform:
        platform = QApplication([])
        run      = platform.exec_
    else:
        run      = lambda: None
    # End Prelude --------------------

    # Setup:
    kis    = Krita.instance()
    doc    = kis.openDocument( "/home/sgaps/.local/share/krita/pykrita/pixel_borders/test_gui/importer_test.kra" )
    win    = kis.openWindow()
    win.qwindow.show()
    layers = doc.topLevelNodes()
    doc.setActiveNode( layers[0] )
    node   = layers[0]
    # Use Quick-Mode and use a custom color (black for this case)
    data = { 
                # Use Quick-Mode:
                "q-recipedsc" : [("force",10)] , "is-quick": True ,
                # Use a custom color (black for this case. BGRA)
                 "colordsc" : ("CS",[0,0,0,255]) ,
                # Use the current data:
                "kis"  : kis ,
                "doc"  : doc ,
                "node" : node
            }
    import time
    # Overrides data:
    gui      = GUI( "Pixel Borders - Test" )
    gui.data = data
    gui.menu.loadPage( "wait" )
    gui.run()
    while not (gui.stop or gui.done): time.sleep(1)

