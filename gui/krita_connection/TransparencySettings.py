# Module:      gui.krita_connection.TransparencySettings.py | [ Language Python ]
# Created by: ( Gaps | sGaps | ArtGaps )
# -------------------------------------------------------------------------------
from PyQt5.QtWidgets import ( QGroupBox , QLabel ,  # Widgets 
                              QFormLayout  )        # Layouts
from PyQt5.QtCore    import pyqtSlot , pyqtSignal
from .Lookup         import kis
from .SpinBox        import SpinBoxFactory

class TransparencySettings( QGroupBox ):
    """
        SIGNALS
            void transparencyChanged( int   )
            void transparencyChanged( float )
            void thresholdChanged   ( int   )
            void thresholdChanged   ( float )
    """
    transparencyChanged = pyqtSignal( [int] , [float] )
    thresholdChanged    = pyqtSignal( [int] , [float] )
    def __init__( self , parent = None ):
        super().__init__( parent )

        # Krita dependency
        depth = kis.activeDocument().activeNode().colorDepth()

        self.setTitle( "Transparency Descriptor" )

        self.Lmain = QFormLayout()
        self.Wtrns = SpinBoxFactory( depth )    # Transparency
        self.Wthrs = SpinBoxFactory( depth )    # Threshold

        self.Wtrns.setValue( self.Wtrns.minimum() )
        self.Wthrs.setValue( self.Wthrs.minimum() )

        self.Lmain.addRow( "Transparency" , self.Wtrns )
        self.Lmain.addRow( "Threshold"    , self.Wthrs )

        self.setLayout( self.Lmain )

        self.Wtrns.valueChanged.connect( self.__transparency_update_request__ )
        self.Wthrs.valueChanged.connect( self.__threshold_update_request__    )

    def setTransparency( self , transparency ):
        self.Wtrns.setValue( transparency )

    def setThreshold( self , threshold ):
        self.Wthrs.setValue( threshold )

    def __transparency_update_request__( self , value ):
        self.transparencyChanged.emit( value )

    def __threshold_update_request__( self , value ):
        self.thresholdChanged.emit( value )
