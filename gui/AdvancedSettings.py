# Module:      gui.Advanced.py | [ Language Python ]
# Created by: ( Gaps | sGaps | ArtGaps )
# --------------------------------------------------
from PyQt5.QtWidgets import ( QGroupBox  , QPushButton ,    # Widgets
                              QVBoxLayout , QHBoxLayout )   # Layouts
from PyQt5.QtCore    import pyqtSlot , pyqtSignal
from .MethodDisplay  import MethodWidget

class AdvancedSettings( QGroupBox ):
    """ Contains additional information about the method.
        SLOTS:
            void hide_buttons()
            void show_butons()
            """
    optionalChanged = pyqtSignal( int )
    def __init__( self , parent = None ):
        super().__init__( parent )
        self.Lmain   = QVBoxLayout()     # Main layout
        self.Lsub    = QHBoxLayout()
        self.Wtable  = MethodWidget()
        self.Badd    = QPushButton( "Add " )
        self.Brem    = QPushButton( "Remove" )

        self.setLayout( self.Lmain )

        self.Lmain.addWidget( self.Wtable )
        self.Lsub.addWidget( self.Brem )
        self.Lsub.addWidget( self.Badd )
        self.Lmain.addLayout( self.Lsub )

        self.setTitle( "Advanced Settings" )


        self.__buttons__ = [ self.Badd , self.Brem ]

        # Connections with add and remove buttons:
        self.Badd.released.connect( self.Wtable.addMethod )
        self.Brem.released.connect( self.Wtable.removeMethod )

    def getData( self ):
        return self.Wtable.getData()

    @pyqtSlot()
    def discardAllExceptFirst( self ):
        for _ in range( self.Wtable.dataLenght() ):
            self.Wtable.removeMethod()

    @pyqtSlot()
    def hide_buttons( self ):
        for b in self.__buttons__:
            b.hide()

    @pyqtSlot()
    def show_butons( self ):
        for b in self.__buttons__:
            b.show()

