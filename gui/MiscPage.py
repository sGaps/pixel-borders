from PyQt5.QtWidgets import QWidget , QSpinBox , QHBoxLayout , QPushButton , QLineEdit , QLabel , QFormLayout
from PyQt5.QtCore    import pyqtSlot , pyqtSignal

from .Page import Page

class ThreshForm( QWidget ):
    def __init__( self , parent = None ):
        super().__init__( parent )
        self.layout = QFormLayout()
        self.setLayout( self.layout )

        self.spin = QSpinBox()
        self.spin.setMinimum( 0   )
        self.spin.setMaximum( 100 )
        self.spin.setSuffix( "%" )
        self.layout.addRow( "Threshold" , self.spin )

    def getPercent( self ):
        return self.spin.value()

class MiscPage( Page ):
    def __init__( self , prevP = None , nextP = None , parent = None ):
        super().__init__( prevP , nextP , parent )
        inv = QPushButton( "Normal Transparency"  )
        ani = QPushButton( "Animation Enabled" )

        self.includeWidget( ani , "animation" )
        self.includeWidget( inv , "invTransp" )
        self.includeWidget( ThreshForm()  , "thresh"    )
        self.invert    = False
        self.animation = True

        inv.released.connect( self.toggleInvert )
        ani.released.connect( self.toggleAnim )

    def toggleAnim( self ):
        anim           = self.getWidget( "animation" )
        self.animation = not self.animation
        if self.animation:
            anim.setText( "Animation Disabled" )
        else:
            anim.setText( "Animation Enabled"  )

    def toggleInvert( self ):
        inv         = self.getWidget( "invTransp" )
        self.invert = not self.invert
        if self.invert:
            inv.setText( "Inverted Transparency" )
        else:
            inv.setText( "Normal Transparency" )

    def getData( self ):
        thr = self.getWidget( "thresh" )
        return { "trdesc" : (self.invert,tr.getPercent()) , "animation" : True }

