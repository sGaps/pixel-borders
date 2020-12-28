from PyQt5.QtCore       import Qt , pyqtSlot , pyqtSignal
from PyQt5.QtWidgets    import ( QSpinBox , QCheckBox , QLabel ,
                                 QWidget , QFormLayout )

from .MenuPage          import MenuPage

class TdscPage( MenuPage ):
    def __init__( self , backP = None , nextP = None , parent = None ):
        super().__init__( backP    = backP  ,
                          nextP    = nextP  ,
                          parent   = parent ,
                          subTitle = "Step 4+: Specify the transparency attributes" )
        #self.inverted = False
        self.invert = QCheckBox()
        self.invert.setChecked( False )

        self.percent  = QSpinBox()
        self.percent.setMinimum( 0   )
        self.percent.setMaximum( 100 )
        self.percent.setSuffix ( "%" )
        self.percent.setAlignment( Qt.AlignRight )

        self.iname = QLabel( "Use Opaque as Transparency" )
        self.pname = QLabel( "Threshold" )
        self.pwidg = QWidget()
        self.pform = QFormLayout( self.pwidg )
        self.pform.setWidget( 0 , QFormLayout.LabelRole , self.iname   )
        self.pform.setWidget( 1 , QFormLayout.LabelRole , self.pname   )
        self.pform.setWidget( 0 , QFormLayout.FieldRole , self.invert  )
        self.pform.setWidget( 1 , QFormLayout.FieldRole , self.percent )

        self.layout.addWidget( self.pwidg  )

    def getData( self ):
        return { "trdesc" : [ self.invert.isChecked() ,     # Take Opaq as Trns
                              self.percent.value()    ] }   # Threshold
