from PyQt5.QtWidgets import QDialog

# Dummy class for the actual GUI:
class DialogBox( QDialog ):
    def __init__( self , parent = None ):
        super().__init__( parent )

    def closeEvent( self , event ):
        event.accept()
