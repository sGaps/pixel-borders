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

DEBUG = True

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
        # Setup thread connections here:
        waitp.accept.clicked.connect( self.menu.accept )

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
        self.menu.page( "wait" ).cancel.setEnabled( False )
        self.stop = True
        self.borderizer.stopRequest()

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
    def sendBorderRequest( self ):
        menu      = self.menu
        # Prevent document modification or deletion while this plugin is running.
        self.changeMenuModal( True )
        menu.raise_()

        # Disable <left| and |right> buttons
        menu.back.setEnabled( False )
        menu.next.setEnabled( False )

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
        self.thread     = QThread()
        self.borderizer = Borderizer( self.arguments )
        border          = self.borderizer
        thread          = self.thread

        # Concurrency:
        border.moveToThread( thread )
        thread.started.connect( border.run )

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
        border.rollbackDone.connect   ( self.onRollback      )
        border.rollbackDone.connect   ( waitp.raiseAccept    )

        # Finishing all:
        # NOTE: (finished -> thread execution end) != (workDone -> task done successfully)
        border.workDone.connect( self.onFinish      )
        border.workDone.connect( thread.quit        )
        border.rollbackDone.connect( thread.quit    ) # Similar to workDone
        thread.finished.connect( border.deleteLater )
        thread.finished.connect( thread.deleteLater )

        # Run:
        thread.start()

    def onFinish( self ):
        w = self.menu.page( "wait" )
        w.subTitle.setText( "Work Done!" )
        w.fstep.hide()
        w.frame.hide()
        self.done = True
        print( "Border Done" , file = stderr )
        self.saveConfig()

    def onRollback( self ):
        w = self.menu.page( "wait" )
        w.fstep.hide()
        w.frame.hide()
        w.subTitle.setText( "Canceled!" )
        print( "Work Canceled" , file = stderr )

    @pyqtSlot( str )
    def reportMessage( self , msg ):
        print( f"[Borderizer]: {msg}" , file = stderr )

    @pyqtSlot()
    def run( self ):
        self.menu.show()

def test( _ ):
    gui  = GUI( "Pixel Borders - Test" )
    gui.run()

def main():
    platform = QApplication([])
    gui  = GUI( "Pixel Borders - Test" )
    gui.run()
    platform.exec_()

if __name__ == "__main__":
    main()
