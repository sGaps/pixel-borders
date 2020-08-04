from PyQt5.QtWidgets import (   # Widgets ------------------
                                QGroupBox , QDialogButtonBox
                                # Layouts ---
                                QHBoxLayout )
class AdvancedSettings( QGroupBox ):
    """ Contains and show a image """
    def __init__( self , width , height , parent = None ):
        super().__init__( parent )
        self.Lmain   = QHBoxLayout()  # Main layout
        self.buttons = QDialogButtonBox( QDialogButtonBox.Ok
                                       | QDialogButtonBox.Cancel )
        self.Lmain.addStretch( 1 )
        self.Lmain.addWidget( self.buttons )

    def connect_on_accepted( self , on_accepted ):
        self.buttons.accepted.connect( on_accepted )

    def connect_on_rejected( self , on_rejected ):
        self.buttons.rejected.connect( on_rejected )
