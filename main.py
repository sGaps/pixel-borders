
from .Context     import CONTEXT , RUN , Extension
from .gui.PxGUI   import GUI

if CONTEXT == "INSIDE_KRITA" & AVAILABLE_BORDERIZER:
    # TODO: Uncomment after merge
    # from .gui.Borderizer import Borderizer
    pass

METADATA = { "SYS_ID"    : "pykrita_pixel_border" ,
             "NAM_ID"    : "Pixel Borders"        ,
             "TOOL_PATH" : "tools/scripts"        ,
             "TITLE"     : "Pixel Borders"        }

DEFAULTSIZE = { "test-body" : (300,100) }
                
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

    def run(self , wparent = None ):
        if CONTEXT == "OUTSIDE_KRITA":
            self.ext = GUI( parent = wparent , title = METADATA["TITLE"] )
            self.ext.run()
            self.setWindowTitle( "Pixel Border - GUI test" )
            self.resize( *DEFAULTSIZE["test-body"] )
            self.show()
            RUN()
        else:
            self.ext = GUI( parent = wparent , title = METADATA["TITLE"] )
            # borderizer = Borderizer()
            # self.ext.setup_borderizer_connection( borderizer )
            self.ext.run()

if __name__ == "__main__":
    p = PixelExtension( None )
    p.run()
