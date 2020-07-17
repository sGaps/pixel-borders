# Module:      GUI.py | [ Language Python ]
# Created by: ( Gaps | sGaps | ArtGaps )
# Using:      ( BBD's Krita Script Starter Feb 2018 )
# ---------------------------------------------------
from PyQt5.QtCore    import ( Qt , QRect )
from .DBox           import DialogBox
from PyQt5.QtWidgets import ( QFormLayout       , QListWidget           , QHBoxLayout   ,
                              QDialogButtonBox  , QVBoxLayout           , QFrame        ,
                              QPushButton       , QAbstractScrollArea   , QLineEdit     ,
                              QMessageBox       , QFileDialog           , QCheckBox     , 
                              QSpinBox          , QComboBox             )
from .core.Borderizer import Borderizer

# Actual GUI class:
class PixelGUI( object ):
    # TODO: Use this for create the elements
    def __init__( self ):
        self.body    = DialogBox()

        # Build Layouts:
        self.layout  = QVBoxLayout( self.body )

        # Build Objects:
        self.buttonBox = QDialogButtonBox( QDialogButtonBox.Ok
                                         | QDialogButtonBox.Cancel )
        # Connect Objects with PixelGUI actions:

    # TODO: Use this for true initialization.
    # NOTE: This is for Layout limits, Range limits, initial state of checkboxes, and others...
    def wake_up( self ):
        pass

