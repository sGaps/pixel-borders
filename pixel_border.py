# Module:      pixel_border.py | [ Language Python ]
# Created by: ( Gaps | sGaps | ArtGaps )
# Using:      ( BBD's Krita Script Starter Feb 2018 )
# ---------------------------------------------------

from krita import Extension
# from .GUI  import PixelGUI

EXTENSION_ID = 'pykrita_pixel_border'
MENU_ENTRY   = 'Pixel Borders'

from PyQt5.QtWidgets import QMessageBox , QWidget
def hello():
    QMessageBox.information( QWidget() , "Tester" , "Hello there!!" )
class PixelExtension( Extension ):
    """
        Wrapper class for the PixelGUI class. This connects 
    """
    def __init__( self , parent ):
        # Initialize this object using the QT C++ interface
        super().__init__( parent )

    def setup( self ):
        pass

    def createActions( self , window ):
        action = window.createAction( EXTENSION_ID , MENU_ENTRY , "tools/scripts" )
        # parameter 1 = the name that Krita uses to identify the action.
        # parameter 2 = the text to be added to the menu entry for this module.
        # parameter 3 = location of menu entry.

        # Set up the actions to krita interface:
        #action.triggered.connect( self.wakeUp )
        action.triggered.connect( hello )

    def wakeUp(self):
        pass
        #self.gui = PixelGUI()
        #self.gui.wakeUp()

