# Module:      gui.krita_connection.SpinBox.py | [ Language Python ]
# Created by: ( Gaps | sGaps | ArtGaps )
# ------------------------------------------------------------------
from PyQt5.QtWidgets import QSpinBox , QDoubleSpinBox

class USpinBox( QSpinBox ):
    def __init__( self , depth = "U8" , parent = None ):
        super().__init__( parent )
        self.setMinimum( 0 )
        if depth == "U8":
            self.setMaximum( 2**8 - 1 )
        else:
            self.setMaximum( 2**16 - 1 )

class FSpinBox( QDoubleSpinBox ):
    def __init__( self , depth = "U8" , parent = None ):
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
    if depth[0] == "U":
        return USpinBox( depth )
    else:
        return FSpinBox( depth )
