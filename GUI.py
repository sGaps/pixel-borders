# Module:      GUI.py | [ Language Python ]
# Created by: ( Gaps | sGaps | ArtGaps )
# Using:      ( BBD's Krita Script Starter Feb 2018 )
# ---------------------------------------------------
from PyQt5.QtCore       import ( Qt , QRect )
# TODO: DELETE THIS BLOCK [BEGIN]
if __name__ == "__main__":
    import sys
    import os
    PACKAGE_PARENT = '..'
    SCRIPT_DIR = os.path.dirname(os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__))))
    sys.path.append(os.path.normpath(os.path.join(SCRIPT_DIR, PACKAGE_PARENT)))
# TODO: DELETE THIS BLOCK [END]

from pixel_border.DBox            import DialogBox  # With this, we can avoid use QWidget::exec_()
#from pixel_border.core.Borderizer import Borderizer
from PyQt5.QtWidgets import QVBoxLayout , QHBoxLayout , QLabel , QPushButton , QComboBox , QLineEdit , QSpinBox , QDialogButtonBox
from PyQt5.QtWidgets import QGroupBox
from PyQt5.QtWidgets import QAbstractItemView , QAbstractScrollArea
from PyQt5.Qt        import Qt

Current_Methods = [
    "Classic" ,
    "Corners" ,
    "Classic then Corners" ,
    "Corners then Classic" ,
    "Classic with Corners" ,
    "Corners with Classic"
]

Initial_Text = "Layer Name"

Advance_Options = {
    0 : "Apply second method after",
    1 : "Combine methods after"
}

"""
    +---------------------------------------------------+
    |                   :                               |
    |   +-----------+   : -Shape Settings-              | <- Title of QGroupBox
    |   | Example   |   :   Method [classic | V ] <2>   |  \                QLabel with QComboBox
    |   |   of   <1>|   :   Name   [____________] <3>   |   |- QGroupBox [  QLabel with QLineEdit
    |   | Method    |   :   Thickness   [1px|V ^] <4>   |  /                QLabel with QSpinBox
    |   +-----------+   :                               |
    |...................................................|
    |   -Color Settings-                                |
    |   [*Use Foreground*] [*Use Background*] <5>       | <- QButtonGroup
    |...................................................|
    |   -Advanced Settings-                             | <- Can be Empty (if is a simple method)
    |   $Description$ [ 1px |V ^] <6>                   | <- Simple QLabel with QSpinBox
    |...................................................|
    |                           <7> [*Cancel*]  [*OK]   |
    +---------------------------------------------------+

"""

# Actual GUI class:
class PixelGUI( object ):
    # TODO: Use QButtonGroup(...) for make the foreground/background color option.
    # TODO: Use QGroupBox(...) instead QVBoxLayout(...) for organize the layouts
    def __init__( self ):
        # Main window:
        self.body         = DialogBox() 
        self.hasAdvance   = True

        # [
        # It will be in the top (right (top) ) box in the window.
        # NOTE: methodCBox.currentIndex() to get the selected index.
        self.methodCBox = QComboBox()
        self.methodCBox.setInsertPolicy    ( QComboBox.InsertAtBottom   )
        self.methodCBox.setSizeAdjustPolicy( QComboBox.AdjustToContents )

        # Use layerName.text() to get its contents
        self.layerName    = QLineEdit()
        self.layerName.setEchoMode ( QLineEdit.Normal )
        self.layerName.setMaxLength( 64 )

        # Use thickness.value() to get its contents
        #  or thickness.cleanText() to get its contents
        self.thickness    = QSpinBox()
        self.thickness.setMinimum(1)
        self.thickness.setSuffix ( "px" )
        self.thickness.setAlignment( Qt.AlignRight )
        
        self.thicknessLabel = QLabel( "Line thickness" )
        self.thicknessLabel.setAlignment( Qt.AlignRight )

        self.actionBox = QDialogButtonBox( QDialogButtonBox.Ok
                                         | QDialogButtonBox.Cancel )

        self.advOption      = QSpinBox()
        self.advOption.setMinimum( 0 )
        self.advOption.setAlignment( Qt.AlignRight )

        self.advOptionLabel = QLabel( "" )
        self.advOptionLabel.setAlignment( Qt.AlignRight )

        self.btop         = QPushButton("top")
        self.bbot         = QPushButton("bot")

        self.mainLayout   = QVBoxLayout()
        self.topLayout    = QHBoxLayout()
        self.topRLayout   = QVBoxLayout()
        self.topRBLayout  = QHBoxLayout()
        self.bottomLayout = QHBoxLayout()

        self.body.setLayout( self.mainLayout )
        
    # TODO: Use this for true initialization.
    # NOTE: This is for Layout limits, Range limits, initial state of checkboxes, and others...
    def initialize( self ):
        self.methodCBox.addItems( Current_Methods )
        self.layerName.setText  ( Initial_Text    )

        self.topLayout.addWidget   ( self.btop )
        self.topRLayout.addWidget  ( self.methodCBox )
        self.topRLayout.addWidget  ( self.layerName  )
        self.topRBLayout.addWidget ( self.thicknessLabel )
        self.topRBLayout.addWidget ( self.thickness  )

        self.bottomLayout.addWidget( self.advOptionLabel )
        self.bottomLayout.addWidget( self.advOption )

        # TODO: THIS GOES INTO CONNECT ACTION

        # Inside mainLayout (Top -> Bottom):
        self.topLayout.addLayout ( self.topRLayout   )
        self.topRLayout.addLayout( self.topRBLayout  )
        self.mainLayout.addLayout( self.topLayout    )
        self.mainLayout.addLayout( self.bottomLayout )

        self.mainLayout.addWidget( self.actionBox )

        self.connect_actions()
        # Top -> Bottom

        self.body.resize( 500 , 300 )
        self.body.setWindowTitle( "Pixel Borders Plugin" )
        self.body.show()
        self.body.activateWindow()

        self.toogle_advanced_options()


    def connect_actions( self ):
        self.methodCBox.currentIndexChanged.connect( self.update_advance )
        self.btop.clicked.connect( self.toogle_advanced_options )

    def update_advance( self ):
        i = self.methodCBox.currentIndex()
        if   i < 2:
            if self.hasAdvance:
                self.toogle_advanced_options()
        elif i < 4:                         # First Then Second
            if not self.hasAdvance:
                self.toogle_advanced_options()
            self.advOptionLabel.setText( Advance_Options[0] )
        else:                               # Combine
            if not self.hasAdvance:
                self.toogle_advanced_options()
            self.advOptionLabel.setText( Advance_Options[1] )

    def toogle_advanced_options( self ):
        if self.hasAdvance:
            self.hasAdvance = False

            self.advOption.hide()
            self.advOptionLabel.hide()

        else:
            self.hasAdvance = True

            self.advOption.show()
            self.advOptionLabel.show()

if __name__ == "__main__":
    p = PixelGUI()
    p.initialize()
