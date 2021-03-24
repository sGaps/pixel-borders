# Module:   gui.TdscPage.py | [ Language Python ]
# Author:   Gaps | sGaps | ArtGaps
# LICENSE:  GPLv3 (available in ./LICENSE.txt)
# -----------------------------------------------
"""
    Defines the Transparency Descriptor page of the Smart Menu.

    [:] Defined in this module
    --------------------------
    TdscPage :: class
        Retrieve information about the transparency properties.

    [*] Author
     |- Gaps : sGaps : ArtGaps
"""

from PyQt5.QtCore       import Qt , pyqtSlot , pyqtSignal
from PyQt5.QtWidgets    import ( QSpinBox , QCheckBox , QLabel ,
                                 QWidget , QFormLayout )

from .MenuPage          import MenuPage , ColorIconButton
from .AnimPage          import AnimPage

class TdscPage( MenuPage ):
    def __init__( self , backP = None , nextP = None , parent = None ):
        super().__init__( backP    = backP  ,
                          nextP    = nextP  ,
                          parent   = parent ,
                          subTitle = "Step 4+: Specify the transparency attributes" )
        self.inverted = False
        self.invert   = ColorIconButton( "Use Opaque as Transparency" , True )
        self.invert.setChecked( False )

        self.percent  = QSpinBox()
        self.percent.setMinimum( 0   )
        self.percent.setMaximum( 100 )
        self.percent.setSuffix ( "%" )
        self.percent.setAlignment( Qt.AlignRight )

        self.pname = QLabel( "Threshold" )
        self.pwidg = QWidget()
        self.pform = QFormLayout( self.pwidg )
        self.pform.setWidget( 1 , QFormLayout.LabelRole , self.pname   )
        self.pform.setWidget( 0 , QFormLayout.FieldRole , self.invert  )
        self.pform.setWidget( 1 , QFormLayout.FieldRole , self.percent )

        self.layout.addWidget( self.pwidg  )
        self.invert.toggled.connect( self.toggle_invert_transparency )

    def toggle_invert_transparency( self ):
        self.inverted = not self.inverted

    def getData( self ):
        return { "trdesc" : [ self.inverted           ,     # Use Opaq as Trnsp
                              self.percent.value()    ] }   # Threshold
