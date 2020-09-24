# Module:      gui.CloseButtons.py | [ Language Python ]
# Created by: ( Gaps | sGaps | ArtGaps )
# ------------------------------------------------------
from PyQt5.QtWidgets import ( QDialogButtonBox , QWidget ,      # Widgets
                              QHBoxLayout )                     # Layouts
from PyQt5.QtCore    import pyqtSlot , pyqtSignal , Qt

class CloseButtons( QWidget ):
    """ Contains and show a image 
        SIGNALS:
            void cancel()
            void accept()
        SLOTS:
            void setEnabled( bool ) """

    cancel = pyqtSignal()
    accept = pyqtSignal()
    def __init__( self , parent = None ):
        super().__init__( parent )
        self.Lmain   = QHBoxLayout()  # Main layout
        self.buttons = QDialogButtonBox( QDialogButtonBox.Ok
                                       | QDialogButtonBox.Cancel )
        self.Lmain.addWidget( self.buttons )

        self.setLayout( self.Lmain )

        self.Lmain.setAlignment( Qt.AlignVCenter | Qt.AlignRight )

        self.buttons.accepted.connect( self.__update_accept_request__ )
        self.buttons.rejected.connect( self.__update_cancel_request__ )

    @pyqtSlot( bool )
    def setEnabled( self , enabled ):
        self.buttons.setEnabled( enabled )

    @pyqtSlot()
    def __update_accept_request__( self ):
        self.accept.emit()

    @pyqtSlot()
    def __update_cancel_request__( self ):
        self.cancel.emit()
