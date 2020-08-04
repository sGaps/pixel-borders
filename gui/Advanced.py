# Module:      gui.Advanced.py | [ Language Python ]
# Created by: ( Gaps | sGaps | ArtGaps )
# --------------------------------------------------
from PyQt5.QtWidgets import (   # Widgets ---------------------
                                QSpinBox , QGroupBox , QLabel ,
                                # Layouts ---
                                QHBoxLayout , QBoxLayout )
from PyQt5.Qt import Qt

ADVDESC = { "sequential" : "Switch to second method application after" ,
            "combinated" : "Start to apply second method after"        ,
            "none"       : ""                                          }

class AdvancedSettings( QGroupBox ):
    """ Contains and show a image """
    def __init__( self , width , height , parent = None ):
        super().__init__( parent )
        self.Lmain = QHBoxLayout()  # Main layout
        self.WOval = QSpinBox()     # Optional Value
        self.Odesc = QLabel()       # Optional Description

        self.set_optional_description( 0 )

        self.setMinimum( 1 )
        self.setMaximum( 1 )
        self.WOval.setAlignment( Qt.AlignRight )
        self.WOval.setMaximumWidth( 80 )

        self.setLayout( self.Lmain )
        self.Lmain.setLayout( QBoxLayout.RightToLeft )
        self.Lmain.addWidget( self.WOval )
        self.Lmain.addWidget( self.WDesc )

        self.setTitle( "Advanced Settings" )
        self.__optional__ = [self.WOval , self.Odesc]
        self.__allw__     = self.__optional__ + []

    def hide_all( self ):
        for w in self.__allw__:
            w.hide()
        self.hide()

    def hide_optional( self ):
        for w in self.__optional__:
            self.hide()

    def show_all( self ):
        for w in self.__allw__:
            self.show()
        self.show()

    def show_optional( self ):
        for w in self.__optional__:
            self.show()

    def optional_value( self ):
        return self.WOval.value()

    def set_optional( self , value )
        self.WOval.setValue( value )

    # TODO: Handle the description update.
    # TODO: Handle the maxValue update.
    def get_optional_description( self , index ):
        if   index < 2: return ADVDESC["none"]
        elif index < 4: return ADVDESC["sequential"]
        elif index < 6: return ADVDESC["combinated"]
        else:           return ADVDESC["none"]

    def set_optional_description( self , index ):
        self.Wdesc.setText( self.getDescription( index ) )

