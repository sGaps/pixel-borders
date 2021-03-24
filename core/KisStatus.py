# Module:   core.KisStatus.py | [ Language Python ]
# Author:   Gaps | sGaps | ArtGaps
# LICENSE:  GPLv3 (available in ./LICENSE.txt)
# -------------------------------------------------
"""
    Defines some useful classes to share data among
    all classes in the Pixel Borders' core.

    [:] Defined in this module
    --------------------------
    ALPHA :: namedtuple( krita.Node , int , QRect )
    FRAME :: namedtuple( krita.Node , int )

    KisStatus :: class
        Holds some values to indicate if the process must
        stop or continue.

    [*] Author
     |- Gaps : sGaps : ArtGaps
"""

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
    """
        Holds some values to indicate if the process must
        stop or continue.
    """
    STOP     = False
    CONTINUE = True
    def __init__( self ):
        super().__init__()
        self.fromGUI  = KisStatus.CONTINUE
        self.fromCore = KisStatus.CONTINUE
        self.mutex    = Lock()    # python's Lock is faster than qmutex.
        self.reasons  = []

    def stopRequest( self ):
        """
            Notify to the current process that it must stop.
            Used in the GUI.
        """
        self.mutex.acquire()
        self.fromGUI = KisStatus.STOP
        self.mutex.release()

    def internalStopRequest( self , why = "" ):
        """
            ARGUMENTS
                why(str): a reason to cancel the proces.

            Notify to the current process that it must stop.
            Used in the core.
        """
        self.mutex.acquire()
        self.fromCore = KisStatus.STOP
        if why: self.reasons.append( why )
        self.mutex.release()

    def showStatus( self , show = (lambda msg: None) ):
        """ 
            ARGUMENTS
                show( function() -> IO () ): abstract notifier where the error message is displayed
            Print the current status and the reasons to cancel the process. """
        self.mutex.acquire()
        for r in self.reasons:
            show( r )
        self.mutex.release()

    def keepRunning( self ):
        """
            RETURNS
                bool
            True if the process hasn't been canceled.
        """
        self.mutex.acquire()
        value = self.fromGUI and self.fromCore
        self.mutex.release()
        return value

