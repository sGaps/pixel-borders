# Module:      gui.Advanced.py | [ Language Python ]
# Created by: ( Gaps | sGaps | ArtGaps )
# --------------------------------------------------
from PyQt5.QtWidgets import ( QSpinBox    , QGroupBox  , QLabel ,   # Widgets
                              QHBoxLayout , QBoxLayout )            # Layouts
from PyQt5.Qt        import Qt
from PyQt5.QtCore    import pyqtSlot , pyqtSignal

ADVDESC = { "sequential" : "Switch to second method application after" ,
            "combinated" : "Start to apply second method after"        ,
            "none"       : ""                                          }

class AdvancedSettings( QGroupBox ):
    """ Contains additional information about the method.
        SIGNALS:
            void optionalChanged( int )
        SLOTS:
            void setMaxOptionalValue( int )
            void hide_all()
            void hide_optional()
            void show_all()
            void show_optional()
            void setOptionalValue( int )        => emits optionalChanged signal
            void setOptionalDescription( int ) """
    optionalChanged = pyqtSignal( int )
    def __init__( self , width , height , parent = None ):
        super().__init__( parent )
        self.Lmain = QHBoxLayout()  # Main layout
        self.WOval = QSpinBox()     # Optional Value
        self.Odesc = QLabel()       # Optional Description

        self.setOptionalDescription( 0 )

        self.WOval.setMinimum( 0 )
        self.WOval.setMaximum( 1 )
        self.WOval.setAlignment( Qt.AlignRight )
        self.WOval.setMaximumWidth( 80 )

        self.setLayout( self.Lmain )
        self.Lmain.setDirection( QBoxLayout.RightToLeft )
        self.Lmain.addWidget( self.WOval )
        self.Lmain.addWidget( self.Odesc )


        self.setTitle( "Advanced Settings" )
        self.__optional__ = [self.WOval , self.Odesc]
        self.__allw__     = self.__optional__ + []

        self.WOval.valueChanged.connect( self.__update_optional_resquest__ )

    @pyqtSlot( int )
    def setMaxOptionalValue( self , value ):
        if self.optionalValue() > value:
            self.WOval.setMaximum( value )
            self.optionalChanged.emit( value )
        else:
            self.WOval.setMaximum( value )

    @pyqtSlot( int )
    def __update_optional_resquest__( self , value ):
        self.optionalChanged.emit( value )

    @pyqtSlot()
    def hide_all( self ):
        for w in self.__allw__:
            w.hide()
        self.hide()

    @pyqtSlot()
    def hide_optional( self ):
        for w in self.__optional__:
            self.hide()

    @pyqtSlot()
    def show_all( self ):
        for w in self.__allw__:
            w.show()
        self.show()

    @pyqtSlot()
    def show_optional( self ):
        for w in self.__optional__:
            w.show()

    def optionalValue( self ):
        return self.WOval.value()

    @pyqtSlot( int )
    def setOptionalValue( self , value ):
        if self.optionalValue() != value:
            self.WOval.setValue( value )
            self.optionalChanged.emit( value )

    def getOptionalDescription( self , index ):
        if   index < 2: return ADVDESC["none"]
        elif index < 4: return ADVDESC["sequential"]
        elif index < 6: return ADVDESC["combinated"]
        else:           return ADVDESC["none"]

    @pyqtSlot( int )
    def setOptionalDescription( self , index ):
        self.Odesc.setText( self.getOptionalDescription( index ) )

