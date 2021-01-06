# Module:      main.py | [ Language Python ]
# Created by: ( Gaps | sGaps | ArtGaps )
# ------------------------------------------
"""
    Main module. It's used to load the package as
    a Krita Extension.

    This defines a PixelExtension object that can
    be used inside and outside Krita.

    [:] Defined in this module
    --------------------------

    PixelExtension  :: class
        Used for manage the gui as a Krita Extension.

    METADATA        :: dict
        Holds relevant information about the module, the path
        and the name of the plugin inside Krita.

    [*] Created By
     |- Gaps : sGaps : ArtGaps
"""

from .Context  import CONTEXT , Extension
from .SetupGUI import GUI

METADATA = { "SYS_ID"    : "pykrita_pixel_border" ,
             "NAM_ID"    : "Pixel Borders"        ,
             "TOOL_PATH" : "tools/scripts"        ,
             "TITLE"     : "Pixel Borders"        }

class PixelExtension( Extension ):
    """ Wrapper class for the GUI class. """

    def __init__( self , parent ):
        # Initialize this object using the QT C++ interface
        super().__init__( parent )

    def setup( self ):
        """ Defined only for compatibility purposes."""
        pass

    def createActions( self , window ):
        """ Used by krita. This makes a valid entry for the plugin in the 'scripts'
            button of Krita"""
        action = window.createAction( METADATA["SYS_ID"]    ,
                                      METADATA["NAM_ID"]    ,
                                      METADATA["TOOL_PATH"] )
        action.triggered.connect( self.run )

    def run( self ):
        """ perform the required actions to run the script in krita. """
        self.ext   = GUI( parent = None , title = METADATA["TITLE"] )
        self.ext.run()


