# Module:      gui.CloseButtons.py | [ Language Python ]
# Created by: ( Gaps | sGaps | ArtGaps )
# ------------------------------------------------------
from PyQt5.QtWidgets import (   # Widgets ::::::::::::::::::
                                QGroupBox , QDialogButtonBox ,
                                # Layouts :::
                                QHBoxLayout )
from PyQt5.QtCore import pyqtSlot , pyqtSignal

class CloseButtons( QGroupBox ):
    """ Contains and show a image """

    cancel = pyqtSignal()
    accept = pyqtSignal()
    def __init__( self , width , height , parent = None ):
        super().__init__( parent )
        self.Lmain   = QHBoxLayout()  # Main layout
        self.buttons = QDialogButtonBox( QDialogButtonBox.Ok
                                       | QDialogButtonBox.Cancel )
        self.Lmain.addWidget( self.buttons )
        self.Lmain.addStretch( 1 )

        self.setLayout( self.Lmain )

        self.buttons.accepted.connect( self.__update_accept_request__ )
        self.buttons.rejected.connect( self.__update_cancel_request__ )

    @pyqtSlot()
    def __update_accept_request__( self ):
        self.accept.emit()

    @pyqtSlot()
    def __update_cancel_request__( self ):
        self.cancel.emit()
