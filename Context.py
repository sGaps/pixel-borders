# CONTEXT HANDLER:
from sys   import stderr
try:
    from krita import Extension
except ImportError:
    print( "[CONTEXT] Unable to find krita. Changing to PyQt5 GUI test." , file = stderr )
    try:
        from PyQt5.QtWidgets import QWidget , QApplication
    except ImportError:
        print( "[CONTEXT] Unable to run PyQt packages." , file = stderr , flush = True )
        CONTEXT   = "NO-REQUIRED-PACKAGES"
        # TODO: remove this and handle other errors outside
        exit(1)
    else:
        krita     = ()
        CONTEXT   = "OUTSIDE_KRITA"
        qMain     = QApplication([])    # Initialize Qt System
        RUN       = qMain.exec_         # Make the script able to run the window.
        Extension = QWidget
else:
    CONTEXT = "INSIDE_KRITA"
    RUN     = lambda : ()
