# Module:      Context.py | [ Language Python ]
# Created by: ( Gaps | sGaps | ArtGaps )
# ---------------------------------------------
""" Utility module for manage and test the GUI inside and outside krita.
    When Krita is available, CONTEXT = 'INSIDE_KRITA'. and all built-in
    functions of krita can be used safely.

    Otherwise, CONTEXT = 'OUTSIDE_KRITA' and you won't be able to use
    Krita functions.

    [:] Defined in this module
    --------------------------
    RUN         :: function
        It's an alias for the exec_ function defined for a QApplication instance.
        Use this after setup all GUI's component.

    Extension   :: class
        It's an QWidget outside Krita. Otherwise it's a Krita.Extension
        Used as base class for the PixelExtension.

    CONTEXT     :: str
        Says when the context is INSIDE_KRITA or OUTSIDE_KRITA.

    [*] Created By 
     |- Gaps : sGaps : ArtGaps
"""
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
        CONTEXT   = "OUTSIDE_KRITA"
        qMain     = QApplication([])    # Initialize Qt System
        RUN       = qMain.exec_         # Make the script able to run the window.
        Extension = QWidget
else:
    CONTEXT = "INSIDE_KRITA"
    RUN     = lambda : ()
