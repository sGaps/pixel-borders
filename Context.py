# Module:      Context.py | [ Language Python ]
# Created by: ( Gaps | sGaps | ArtGaps )
# ---------------------------------------------
""" Utility module for manage and test the GUI inside and outside krita."""
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
    else:
        krita     = ()
        CONTEXT   = "OUTSIDE_KRITA"
        qMain     = QApplication([])    # Initialize Qt System
        RUN       = qMain.exec_         # Make the script able to run the window.
        Extension = QWidget
else:
    CONTEXT = "INSIDE_KRITA"
    RUN     = lambda : ()
