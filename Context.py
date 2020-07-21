# CONTEXT HANDLER:
try:
    from krita import Extension
except ImportError:
    print( "Unable to find krita. Changing to PyQt5 GUI test." )
    try:
        from PyQt5.QtWidgets import QWidget , QApplication
    except ImportError:
        print( "Unable to run PyQt packages." )
        exit(1)
    else:
        CONTEXT   = "OUTSIDE_KRITA"
        qMain     = QApplication([])    # Initialize Qt System
        RUN       = qMain.exec_         # Make the script able to run the window.
        Extension = QWidget
else:
    CONTEXT = "INSIDE_KRITA"
    RUN     = lambda : ()
    print( "Using Krita Interface." )

