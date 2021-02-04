from PyQt5.QtCore       import pyqtSlot , pyqtSignal
from PyQt5.QtWidgets    import ( QWidget , QCheckBox , QSpinBox ,
                                 QLabel , QFormLayout )

from .MenuPage          import MenuPage , buttonWithIcon
from .MethodDisplay     import MethodWidget

from .krita_connection.Lookup import KRITA_AVAILABLE , dprint
if KRITA_AVAILABLE:
    from krita import Krita

# Pre: { KRITA_AVAILABLE = True }
class AnimPage( MenuPage ):
    def __init__( self , backP = None , nextP = None , parent = None ):
        super().__init__( backP    = backP  ,
                          nextP    = nextP  ,
                          parent   = parent ,
                          subTitle = "Step 4++: Animation Time!" )
        # Override all config (Because it's quick configuration)
        self.override = True
        self.defValue = []

        self.animate = True
        self.tryAnim = buttonWithIcon( "Try Animate" , True )
        self.tryAnim.setChecked( True )

        self.start   = QSpinBox()
        self.start.setMinimum( 0 )
        self.start.setValue ( self.start.minimum() )

        self.finish  = QSpinBox()
        self.finish.setMinimum( 0 )
        self.finish.setValue( self.finish.maximum() )

        self.sname   = QLabel( "Start Time" )
        self.fname   = QLabel( "Finish Time" )

        self.fwidg = QWidget()
        self.ftime = QFormLayout( self.fwidg )
        self.ftime.setWidget( 0 , QFormLayout.LabelRole , self.sname   )
        self.ftime.setWidget( 1 , QFormLayout.LabelRole , self.fname   )
        self.ftime.setWidget( 0 , QFormLayout.FieldRole , self.start   )
        self.ftime.setWidget( 1 , QFormLayout.FieldRole , self.finish  )
        self.ftime.setWidget( 2 , QFormLayout.FieldRole , self.tryAnim )

        self.layout.addWidget( self.fwidg )

        # Minimal time connections:
        self.start.valueChanged.connect ( self.finish.setMinimum )
        self.finish.valueChanged.connect( self.start.setMaximum  )
        self.tryAnim.toggled.connect    ( self.setTimeEnabled    )

    @pyqtSlot()
    def toggle_tryAnimate( self ):
        self.animate = not self.animate

    @pyqtSlot( bool )
    def setTimeEnabled( self , boolean_value ):
        self.start.setEnabled( boolean_value )
        self.finish.setEnabled( boolean_value )

    @pyqtSlot( bool )
    def setOverride( self , boolean_value ):
        self.override = boolean_value

    def connect_with_krita( self ):
        if KRITA_AVAILABLE:
            # Take the current Document:
            doc = Krita.instance().activeDocument()
            if not doc:
                dprint( "[Pixel Anim.Page]: There isn't any document." )
                self.defValue = [ self.start.minimum()  ,
                                  self.finish.maximum() ]
            else:
                # Take the whole timeline:
                self.defValue = [ doc.fullClipRangeStartTime() ,    # Max Start Time
                                  doc.fullClipRangeEndTime  () ]    # Max End Time
                # Update the bounds:
                self.start.setMinimum ( self.defValue[0] )
                self.finish.setMaximum( self.defValue[1] )
        else:
            dprint( "[Pixel Anim.Page]: Unable to connect with Krita." )
        self.start.setValue ( self.start.minimum() )
        self.finish.setValue( self.finish.maximum() )

    def getData( self ):
        if KRITA_AVAILABLE and self.override:
            return { "animation"   : self.defValue ,            # [Start, Finish]
                     "try-animate" : True }                     # Always try animate
        else:
            return { "animation" : [ self.start.value()  ,      # Start
                                     self.finish.value() ]    , # Finish
                     "try-animate" : self.animate        }
