from PyQt5.QtWidgets import QSpinBox , QDoubleSpinBox

class USpinBox( QSpinBox ):
    def __init__( self , depth = "U8" , parent = None ):
        super().__init__( parent )
        self.setMinimum( 0 )
        if depth == "U8":
            self.setMaximum( 2**8 )
        else:
            self.setMaximum( 2**16 )

class FSpinBox( QDoubleSpinBox ):
    def __init__( self , depth = "U8" , parent = None ):
        super().__init__( parent )
        self.setMinimum( 0.0 )
        self.setMaximum( 1.0 )

        # Search how many decimals use krita
        if depth == "F16":
            self.setDecimals( 9 )
        else:
            self.setDecimals( 15 )

def SpinBoxFactory( depth ):
    if depth[0] == "U":
        return USpinBox( depth )
    else:
        return FSpinBox( depth )
