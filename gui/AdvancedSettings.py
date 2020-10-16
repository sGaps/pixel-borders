# Module:      gui.AdvancedSettings.py | [ Language Python ]
# Created by: ( Gaps | sGaps | ArtGaps )
# ----------------------------------------------------------
from PyQt5.QtWidgets import ( QGroupBox  , QPushButton , QLabel ,    # Widgets
                              QVBoxLayout , QHBoxLayout )   # Layouts
from PyQt5.QtCore    import pyqtSlot , pyqtSignal
from .MethodDisplay  import MethodWidget

class AdvancedSettings( QGroupBox ):
    """ Contains additional information about the method.
        SIGNALS:
            void firstMethodChanged( str )
        SLOTS:
            void hide_buttons()
            void show_butons()
            void cellBeingEdited( int , int )
    """
    firstMethodChanged = pyqtSignal( str )
    cellBeingEdited    = pyqtSignal( int , int )

    def __init__( self , parent = None ):
        super().__init__( parent )
        self.Lmain   = QVBoxLayout()     # Main layout
        self.Lsub    = QHBoxLayout()
        self.Wtable  = MethodWidget()
        self.Badd    = QPushButton( "Add " )
        self.Brem    = QPushButton( "Remove" )
        self.Winfo   = QLabel( "Press click in an entry to edit its contents" )

        self.setLayout( self.Lmain )

        self.Lmain.addWidget( self.Winfo )
        self.Lmain.addWidget( self.Wtable )
        self.Lsub.addWidget( self.Brem )
        self.Lsub.addWidget( self.Badd )
        self.Lmain.addLayout( self.Lsub )

        self.setTitle( "Advanced Settings" )

        self.__buttons__ = [ self.Badd , self.Brem ]

        # Connections with add and remove buttons:
        self.Badd.released.connect( self.Wtable.addMethod )
        self.Brem.released.connect( self.Wtable.removeMethod )

        self.Wtable.firstMethodChanged.connect(
                self.__first_method_change_update_request__ )
        self.Wtable.cellBeingEdited.connect( 
                self.__cell_being_edited_update_request__ )

    @pyqtSlot( int , int )
    def __cell_being_edited_update_request__( self , row , col ):
        self.cellBeingEdited.emit( row , col )

    @pyqtSlot( str )
    def __first_method_change_update_request__( self , method ):
        self.firstMethodChanged.emit( method )

    def dataLength( self ):
        return self.Wtable.dataLength()

    def getCellContent( self , row , col ):
        return self.Wtable.getUnsafeData()[row][col]

    def getData( self ):
        return self.Wtable.getData()

    def setRecipe( self , recipe ):
        return self.Wtable.setRecipe( recipe )

    @pyqtSlot()
    def discardAllExceptFirst( self ):
        for _ in range( self.Wtable.dataLength() - 1 ):
            self.Wtable.removeMethod()

    @pyqtSlot()
    def hide_buttons( self ):
        for b in self.__buttons__:
            b.hide()

    @pyqtSlot()
    def show_buttons( self ):
        for b in self.__buttons__:
            b.show()

