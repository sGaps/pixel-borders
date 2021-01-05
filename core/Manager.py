try:
    from krita              import Selection , Krita , ManagedColor
except:
    print( "[Arguments] Krita Not available" )
from .Arguments import KisData
from PyQt5.QtCore       import QRect , QObject , pyqtSlot , pyqtSignal , QMutex

class KritaManager( QObject ):
    safeImportRequest     = pyqtSignal( [str] , int , int )
    safeUpdateTimeRequest = pyqtSignal( int )
    # ----------- RESERVED ----------- #
    exclusiveDone         = pyqtSignal()
    # -------------------------------- #
    def __init__( self , arguments = KisData() , lock = QMutex() , parent = None ):
        super().__init__( parent )
        self.args = arguments
        self.doc  = arguments.doc
        self.kis  = arguments.kis
        self.win  = arguments.win
        self.view = arguments.view
        self.shared    = lock
        self.exclusive = QMutex()
        self.safeImportRequest.connect( self.self_safeImportAnimation )
        self.exclusiveDone.connect    ( self.self_resetExclusive      )
        self.safeImportRequest.connect( self.self_updateCurrentTime   )

        # Has rights for go first with exclusive
        self.exclusive.lock()

    @pqtSlot()
    def self_resetExclusive( self ):
        self.exclusive.unlock()
        self.exclusive.lock()

    @pyqtSlot( [str] , int , int )
    def self_safeImportAnimation( self , framenames , startframe , step ):
        self.ret = self.doc.importAnimation( framenames , startframe , step )
        self.exclusive.unlock()

    @pyqtSlot( int )
    def self_updateCurrentTime( self , time ):
        self.doc.setCurrentTime( time )
        self.exclusive.unlock()

    # NOTE: Can must be used in a different thread.
    def extr_waitForDone( self ):
        # Permission to continue:
        self.exclusive.lock()
        val = self.ret
        self.exclusive.unlock()
        self.exclusiveDone.emit()
        return self.ret # Return any value from the last exclusive operation

    # NOTE: Can must be used in a different thread.
    def extr_syncSafeImportFrames( self , framenames , startframe , step ):
        self.safeImportRequest.emit( framenames , startframe , step )
        return self.extr_waitForDone()

    @pyqtSlot( int )
    def extr_syncUpdateCurrentTime( self , time ):
        self.safeUpdateTimeRequest.emit( time )
        self.extr_waitForDone()
