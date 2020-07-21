# Run this script as a package.
if __name__ == "__main__":
    import sys
    from os import path , getcwd
    PACKAGE_PARENT = '..'
    SCRIPT_DIR = path.dirname( path.realpath(path.join( getcwd() , path.expanduser(__file__) )) )
    sys.path.append(path.normpath( path.join( SCRIPT_DIR , PACKAGE_PARENT ) ))

from Context import CONTEXT , RUN , Extension
from PxGUI   import GUI

METADATA = { "SYS_ID"    : "pykrita_pixel_border" ,
             "BAR_ID"    : "Pixel Borders"        ,
             "TOOL_PATH" : "tools/scripts"        }

DEFAULTSIZE = { "test-body" : (300,100) ,
                "extension" : (446,304) }   # layoutBody.sizeHint() = (446,382) with Advanced options -> (446,304) when selects a simple method again.

# TODO: Need a way to kill this thread when the GUI finish its tasks.
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
        action = window.createAction( METADATA["SYS_ID"] , METADATA["BAR_ID"] , METADATA["TOOL_PATH"] )
        action.triggered.connect( hello )

    def run(self):
        self.ext = GUI( *DEFAULTSIZE["extension"] , parent = self )
        self.ext.run()

        if CONTEXT == "OUTSIDE_KRITA":
            self.setWindowTitle( "Pixel Border - GUI test" )
            self.resize( *DEFAULTSIZE["test-body"] )
            self.show()
            # TODO Connect the close event here
            #self.close.connect( self.ext.name_of_exit_method )

if __name__ == "__main__":
    p = PixelExtension( None )
    p.run()
    RUN()
