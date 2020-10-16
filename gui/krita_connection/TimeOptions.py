# Module:      gui.krita_connection.SpinBox.py | [ Language Python ]
# Created by: ( Gaps | sGaps | ArtGaps )
# ------------------------------------------------------------------
"""
    Defines a widget used in the PxGUI when krita is available.

    [:] Defined in this module
    --------------------------

    TimeOptions :: class
        Widget used to display animation/time information.

    [*] Created By 
     |- Gaps : sGaps : ArtGaps
"""



from PyQt5.QtWidgets import ( QSpinBox     , QGroupBox , QLabel ,   # Widgets 
                              QFormLayout  )                        # Layouts
from PyQt5.QtCore    import pyqtSlot , pyqtSignal
from .Lookup         import kis

class TimeOptions( QGroupBox ):
    """
        SIGNALS
            void startTimeChanged( int  )
            void endTimeChanged  ( int  )
            void enabledAnimation ( bool )
    """
    startTimeChanged = pyqtSignal( int  )
    endTimeChanged   = pyqtSignal( int  )
    enabledAnimation = pyqtSignal( bool )
    def __init__( self , parent = None ):
        super().__init__( parent )
        doc = kis.activeDocument()

        self.timeline = ( doc.fullClipRangeStartTime() ,
                          doc.fullClipRangeEndTime()   )
        self.Lmain    = QFormLayout()
        self.WStart   = QSpinBox()
        self.WEnd     = QSpinBox()

        self.setTitle( "Enable Animation" )
        self.setCheckable( True )
        self.setChecked( True )

        self.Lmain.addRow( "Start Time" , self.WStart )
        self.Lmain.addRow( "End   Time" , self.WEnd   )

        self.WStart.setMinimum( self.timeline[0] )
        self.WEnd.setMinimum( self.timeline[0] )

        self.WStart.setMaximum( self.timeline[1] )
        self.WEnd.setMaximum( self.timeline[1] )

        self.WStart.setValue( self.timeline[0] )
        self.WEnd.setValue( self.timeline[1] )

        self.setLayout( self.Lmain )

        self.WEnd.valueChanged.connect( self.WStart.setMaximum )
        self.WStart.valueChanged.connect( self.WEnd.setMinimum )

        self.WStart.valueChanged.connect( self.__start_time_update_request__ )
        self.WEnd.valueChanged.connect  ( self.__end_time_update_request__   )
        self.toggled.connect( self.__enable_animation_update_request__ )

    def __start_time_update_request__( self , time ):
        self.startTimeChanged.emit( time )

    def __end_time_update_request__( self , time ):
        self.endTimeChanged.emit( time )

    def __enable_animation_update_request__( self , permit ):
        self.enabledAnimation.emit( permit )

    def getTime( self ):
        return [ self.WStart.value() , self.WEnd.value() ]

