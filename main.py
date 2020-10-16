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



from .Context     import CONTEXT , RUN , Extension
from .gui.PxGUI   import GUI

if CONTEXT == "INSIDE_KRITA": from .core.Borderizer import Borderizer

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

    # TODO: This function is called twice everytime the action connected to run. Fix it.
    def run( self ):
        """ Performs all the required actions to build the GUI itself and the Borderizer object
            when Krita is available. Else, This only builds a GUI for testing purposes.

            NOTE: This requires that you have installed PyQt5 module on your system. """
        if CONTEXT == "OUTSIDE_KRITA":
            self.ext = GUI( parent = None , title = METADATA["TITLE"] )
            self.ext.run()
            self.setWindowTitle( "Pixel Border - GUI test" )
            self.resize( *DEFAULTSIZE["test-body"] )
            self.show()
            RUN()
        else:
            self.ext   = GUI( parent = None , title = METADATA["TITLE"] )
            borderizer = Borderizer( cleanUpAtFinish = False )
            self.ext.setup_borderizer_connection( borderizer )
            self.ext.run()

