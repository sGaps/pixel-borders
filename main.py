# Module:      main.py | [ Language Python ]
# Created by: ( Gaps | sGaps | ArtGaps )
# ------------------------------------------
from .Context     import CONTEXT , RUN , Extension
from .gui.PxGUI   import GUI

if CONTEXT == "INSIDE_KRITA":
     from .core.Borderizer import Borderizer

METADATA = { "SYS_ID"    : "pykrita_pixel_border" ,
             "NAM_ID"    : "Pixel Borders"        ,
             "TOOL_PATH" : "tools/scripts"        ,
             "TITLE"     : "Pixel Borders"        }

class PixelExtension( Extension ):
    """
        Wrapper class for the GUI class.
    """
    def __init__( self , parent ):
        # Initialize this object using the QT C++ interface
        super().__init__( parent )

    def setup( self ):
        pass

    def createActions( self , window ):
        action = window.createAction( METADATA["SYS_ID"]    , 
                                      METADATA["NAM_ID"]    ,
                                      METADATA["TOOL_PATH"] )
        action.triggered.connect( self.run )

    # TODO: This function is called twice everytime the action connected to run. Fix it.
    def run( self ):
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

