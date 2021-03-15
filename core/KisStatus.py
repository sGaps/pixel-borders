from threading   import Lock , Condition
from collections import namedtuple

class ALPHA(
    namedtuple(
        typename    = 'ALPHA',
        field_names = ['alpha','time','bounds']
              )
           ): pass
class FRAME(
    namedtuple(
        typename    = 'FRAME',
        field_names = ['node','time']
              )
           ): pass

class KisStatus( object ):
    STOP     = False
    CONTINUE = True
    def __init__( self ):
        super().__init__()
        self.fromGUI  = KisStatus.CONTINUE
        self.fromCore = KisStatus.CONTINUE
        self.mutex    = Lock()    # python's Lock is faster than qmutex.
        self.reasons  = []

    def stopRequest( self ):
        self.mutex.acquire()
        self.fromGUI = KisStatus.STOP
        self.mutex.release()

    def internalStopRequest( self , why = "" ):
        self.mutex.acquire()
        self.fromCore = KisStatus.STOP
        if why: self.reasons.append( why )
        self.mutex.release()

    def showStatus( self , show = (lambda msg: None) ):
        self.mutex.acquire()
        for r in self.reasons:
            show( r )
        self.mutex.release()

    def keepRunning( self ):
        self.mutex.acquire()
        value = self.fromGUI and self.fromCore
        self.mutex.release()
        return value

