
# TODO: Delete this block
# Run this script as a package.
if __name__ == "__main__":
    import sys
    from os import path , getcwd
    PACKAGE_PARENT = '..'
    SCRIPT_DIR = path.dirname( path.realpath(path.join( getcwd() , path.expanduser(__file__) )) )
    sys.path.append(path.normpath( path.join( SCRIPT_DIR , PACKAGE_PARENT ) ))
    from pixel_border.Context     import CONTEXT , RUN , Extension
    from pixel_border.gui.PxGUI   import GUI
else:
    from .Context     import CONTEXT , RUN , Extension
    from .gui.PxGUI   import GUI

if CONTEXT == "INSIDE_KRITA":
    # TODO: Import the borderizer later
    # Connect manually the import
    Connect = True
else:
    Connect = False

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
            self.ext.run()

if __name__ == "__main__":
    p = PixelExtension( None )
    p.run()
