# Module:      gui.Settings.py | [ Language Python ]
# Created by: ( Gaps | sGaps | ArtGaps )
# --------------------------------------------------
from PyQt5.QtWidgets import (   # Widgets ::::::::::::::::::::::::::::::::::::
                                QComboBox , QLineEdit , QSpinBox , QGroupBox , QWidget ,
                                # Layouts ::::::::::::::::::::::::::::::::
                                QVBoxLayout , QHBoxLayout , QFormLayout  )
from PyQt5.Qt import Qt         # Constants
from .Image   import Preview    # Image manager
from PyQt5.QtCore import pyqtSlot , pyqtSignal

# CONSTANTS ----------------------------
METHODS = { 0 : "Classic"              ,
            1 : "Corners"              ,
            2 : "Classic then Corners" ,
            3 : "Corners then Classic" ,
            4 : "Classic with Corners" ,
            5 : "Corners with Classic" }

# TODO: Implement some methods with signals:like
#       @pyqtSlot("name-slot")
#       def method( self , value ): pass
class ImageDisplay( QGroupBox ):
    """ Contains and show a image
        SIGNALS:
            void imageChanged( int )
        SLOTS:
            void select_image( int )
            void load_image_from( str )
    """
    imageChanged = pyqtSignal( int )

    def __init__( self , width , height , parent = None ):
        super().__init__( parent )
        self.Lmain = QVBoxLayout()
        self.image = Preview()
        self.Lmain.addWidget( self.image )

        self.setTitle( "Preview" )
        self.setLayout( self.Lmain )
        self.__setup_size__( width , height )

    def __setup_size__( self , width , height ):
        pass

    @pyqtSlot( int )
    def select_image( self , index ):
        self.image.setIconFromIndex( index )
        self.imageChanged.emit( index )

    @pyqtSlot( str )
    def load_image_from( self , relative_path ):
        self.image.loadImg( relative_path )
        self.imageChanged.emit( -1 )

MAXNAMELENGTH = 64 
EDITNAMEMODE  = QLineEdit.Normal

# TODO: Add Signals and slots
class BasicInfo( QGroupBox ):
    """ Retrieve basic information about the method.
        SIGNALS:
            void methodChanged( int )
            void nameChanged( str )
            void thicknessChanged( int )
        SLOTS:
            void setMethod( int )       => emits a methodChanged signal
            void setName( str )         => emits a nameChanged signal
            void setThickness( int )    => emits a thicknessChanged signal
    """
    methodChanged    = pyqtSignal( int )
    nameChanged      = pyqtSignal( str )
    thicknessChanged = pyqtSignal( int )

    def __init__( self , width , height , values = METHODS , parent = None ):
        super().__init__( parent )
        self.Lmain   = QFormLayout()
        self.Wname   = QLineEdit()
        self.Wmethod = QComboBox()
        self.Wthickn = QSpinBox()

        self.Wname.setMaxLength( 64 )
        self.Wname.setEchoMode ( QLineEdit.Normal )

        self.Wmethod.setInsertPolicy    ( QComboBox.InsertAtBottom   )
        self.Wmethod.setSizeAdjustPolicy( QComboBox.AdjustToContents )
        self.Wmethod.addItems           ( METHODS.values()           )
        self.Wmethod.setCurrentIndex    ( 0                          )

        self.Wthickn.setMinimum( 1    )
        self.Wthickn.setMaximum( 200  )
        self.Wthickn.setSuffix ( "px" )
        self.Wthickn.setAlignment( Qt.AlignRight )

        self.Lmain.setLabelAlignment( Qt.AlignLeft | Qt.AlignVCenter )

        self.Lmain.addRow( "Method"         , self.Wmethod )
        self.Lmain.addRow( "Layer Name"     , self.Wname   )
        self.Lmain.addRow( "Line thickness" , self.Wthickn )

        self.setTitle( "Settings" )
        self.setLayout( self.Lmain )
        self.__setup_size__( width , height )

        self.Wname.textChanged.connect( self.__update_name_request__ )
        self.Wthickn.valueChanged.connect( self.__update_thickness_request__ )
        self.Wmethod.currentIndexChanged.connect( self.__update_method_request__ )

    @pyqtSlot( str )
    def __update_name_request__( self , name ):
        self.nameChanged.emit( name )

    @pyqtSlot( int )
    def __update_thickness_request__( self , thickness ):
        self.thicknessChanged.emit( thickness )

    @pyqtSlot( int )
    def __update_method_request__( self , index ):
        self.methodChanged.emit( index )

    def __setup_size__( self , width , height ):
        pass

    @pyqtSlot( str )
    def setName( self , name ):
        if self.name() != name:
            self.Wname.setText( name )
            self.nameChanged.emit( name )

    def name( self ):
        return self.Wname.text()

    @pyqtSlot( int )
    def setMethod( self , index ):
        if self.method() != index:
            self.Wmethod.setCurrentIndex( index )
            self.methodChanged.emit( index )


    def method( self ):
        return self.Wmethod.currentIndex()

    @pyqtSlot( int )
    def setThickness( self , thickness ):
        if self.thickness() != thickness:
            self.Wmethod.setValue( thickness )
            self.thicknessChanged.emit( index )

    def thickness( self ):
        return self.Wmethod.value()
    
# TODO: Add slots for signals.
class SettingsDisplay( QWidget ):
    """ Retrieve information about the method and display an image.
        SIGNALS:
            void methodChanged( int )
            void nameChanged( str )
            void thicknessChanged( int )
        SLOTS:
            void setMethod( int )       => emits a methodChanged signal
            void setName( str )         => emits a nameChanged signal
            void setThickness( int )    => emits a thicknessChanged signal
    """
    methodChanged    = pyqtSignal( int )
    nameChanged      = pyqtSignal( str )
    thicknessChanged = pyqtSignal( int )
    def __init__( self , width , height , mvalues = METHODS , parent = None ):
        super().__init__( parent )
        proportions = { "left" : ( width * 1 , height * 1 ) , "right" : ( width * 1 , height * 1 ) }
        self.Lmain  = QHBoxLayout()
        self.WLeft  = ImageDisplay( proportions["left"][0] , proportions["left"][1] )
        self.WRight = BasicInfo   ( proportions["right"][0]   , proportions["right"][1] , values = mvalues )

        self.Lmain.addWidget( self.WLeft  )
        self.Lmain.addWidget( self.WRight )
        self.Lmain.addStretch(1)
        self.WLeft.select_image( self.WRight.method() )

        self.setLayout( self.Lmain )
        self.__setup_size__( width , height )

        self.WRight.nameChanged.connect( self.__update_name_request__ )
        self.WRight.thicknessChanged.connect( self.__update_thickness_request__ )
        self.WRight.methodChanged.connect( self.__update_method_request__ )

        self.WRight.methodChanged.connect( self.WLeft.select_image )


    @pyqtSlot( str )
    def __update_name_request__( self , name ):
        self.nameChanged.emit( name )

    @pyqtSlot( int )
    def __update_thickness_request__( self , thickness ):
        self.thicknessChanged.emit( thickness )

    @pyqtSlot( int )
    def __update_method_request__( self , index ):
        self.methodChanged.emit( index )

    def __setup_size__( self , width , height ):
        pass

    @pyqtSlot( int )
    def setName( self , name ):
        if self.name() == name:
            self.WRight.setName( name )
            self.nameChanged.emit( name )

    def name( self ):
        return self.WRight.name()

    @pyqtSlot( int )
    def setMethod( self , index ):
        if self.method() == index:
            self.WRight.setMethod( index )
            self.methodChanged.emit( index )

    def method( self ):
        return self.WRight.method()

    @pyqtSlot( int )
    def setThickness( self , thickness ):
        if self.thickness() == thickness:
            self.WRight.setThickness( thickness )
            self.thicknessChanged.emit( thickness )

    def thickness( self ):
        self.WRight.thickness()

