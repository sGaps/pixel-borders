# Module:      gui.krita_connection.SpinBox.py | [ Language Python ]
# Created by: ( Gaps | sGaps | ArtGaps )
# ------------------------------------------------------------------
"""
    Utility module that defines some useful spinboxes.

    [:] Defined in this module
    --------------------------
    USpinBox        :: class
        Unsigned spinbox.

    FSpinBox        :: class
        Float spinbox.

    SpinBoxFactory  :: function
        Uses a colorDepth string to returns a Unsigned or Float spinbox.

    [*] Created By 
     |- Gaps : sGaps : ArtGaps
"""
from PyQt5.QtWidgets import QSpinBox , QDoubleSpinBox

class USpinBox( QSpinBox ):
    """ Unsigned spinbox [char or short]"""
    def __init__( self , depth = "U8" , parent = None ):
        super().__init__( parent )
        self.setMinimum( 0 )
        if depth == "U8":
            self.setMaximum( 2**8 - 1 )
        else:
            self.setMaximum( 2**16 - 1 )

class FSpinBox( QDoubleSpinBox ):
    def __init__( self , depth = "U8" , parent = None ):
        """ Float spinbox [float]"""
        super().__init__( parent )
        self.setMinimum( 0.0 )
        self.setMaximum( 1.0 )

        # Search how many decimals use krita
        if depth == "F16":
            # Previous: 7
            self.setDecimals( 6 )   # Krita uses 6 decimals
        else:
            # Previous: 15
            self.setDecimals( 6 )   # Krita uses 6 decimals

def SpinBoxFactory( depth ):
    """
        ARGUMENTS
            depth(str): used to see wich Spinbox will be returned.
        RETURNS
            a subclass of QSpinBox (USpinBox or FSpinBox)
    """
    if depth[0] == "U":
        return USpinBox( depth )
    else:
        return FSpinBox( depth )
