# Module:      gui.Settings.py | [ Language Python ]
# Created by: ( Gaps | sGaps | ArtGaps )
# --------------------------------------------------
from PyQt5.QtWidgets import (   # Widgets ------------------------------------
                                QComboBox , QLineEdit , QSpinBox , QGroupBox , 
                                # Layouts --------------------------------
                                QVBoxLayout , QHBoxLayout , QFormLayout  )
from PyQt5.Qt import Qt         # Constants
from .Image   import Preview    # Image manager

# CONSTANTS ----------------------------
METHODS = { 0 : "Classic"              ,
            1 : "Corners"              ,
            2 : "Classic then Corners" ,
            3 : "Corners then Classic" ,
            4 : "Classic with Corners" ,
            5 : "Corners with Classic" }

class ImageDisplay( QGroupBox ):
    """ Contains and show a image """
    def __init__( self , width , height , parent = None ):
        super().__init__( parent )
        self.Lmain = QVBoxLayout()
        self.image = Preview()
        self.Lmain.addWidget( self.image )

        self.setTittle( "Preview" )
        self.setLayout( self.Lmain )
        self.__setup_size__( width , height )

    def __setup_size__( self , width , height ):
        pass

    def select_image( self , index ):
        self.image.setIconFromIndex( index )

    def load_image_from( self , relative_path ):
        self.image.loadImg( relative_path )

MAXNAMELENGTH = 64 
EDITNAMEMODE  = QLineEdit.Normal
class BasicInfo( QGroupBox ):
    """ Retrieve basic information about the method. """
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
        self.Lmain.addStretch( 1 )

        self.setTittle( "Settings" )
        self.setLayout( self.Lmain )
        self.__setup_size__( width , height )

    def __setup_size__( self , width , height ):
        pass

    def setName( self , name ):
        self.Wname.setText( name )

    def name( self ):
        return self.Wname.text()

    def setMethod( self , index ):
        self.Wmethod.setCurrentIndex( index )

    def method( self ):
        return self.Wmethod.currentIndex()

    def setThickness( self , thickness ):
        self.Wmethod.setValue( thickness )

    def thickness( self )
        return self.Wmethod.value()
    
class SettingsDisplay( QGroupBox ):
    """ Retrieve information about the method and display an image. """
    def __init__( self , width , height , mvalues = METHODS , parent = None ):
        super().__init__( parent )
        proportions = { "left" : ( width * 1 , height * 1 ) , "right" : ( width * 1 , height * 1 ) }
        self.Lmain  = QHBoxLayout()
        self.WLeft  = ImageDisplay( proportions["left"] )
        self.WRight = BasicInfo   ( proportions["right"] , values = mvalues )

        self.Lmain.addWidget( self.WLeft  )
        self.Lmain.addWidget( self.WRight )

        self.setLayout( self.Lmain )
        self.__setup_size__( width , height )

    def __setup_size__( self , width , height ):
        pass

    def connect_to_updates( self , on_method_change , on_name_change , on_thickness_change ):
        """ This connects the actions will to perform after
            the update of any widget. """
        self.connect_to_method( on_method_change )
        self.connect_to_name  ( on_name_change   )
        self.connect_to_thickness( on_thickness_change )

    def connect_to_method( self , on_method_change ):
        self.WRight.Wmethod.currentIndexChanged.connect( on_method_change )

    def connect_to_name( self, on_name_change ):
        self.WRight.Wname.textChanged.connect( on_name_change )

    def connect_to_thickness( self , on_thickness_change ):
        self.WRight.Wthickn.valueChanged.connect( on_thickness_change )

    def __method_update__( self ):
        index = self.method()
        self.data["method"] = index
        self.WLeft.select_image( index )

    def __name_updata__( self ):
        self.data["name"] = self.name()

    def __thickness_update__( self ):
        self.data["thickness"] = self.thickness()

    # TODO: Handle the advanced settings display later.
    # TODO: Handle the max value of advanced settings (application) later.
    # TODO: Handle the advanced description display later
    def auto_connect_with_data( self , data ):
        self.data = data
        self.connect_to_method( self.__method_update__ )
        self.connect_to_name  ( self.__name_update__   )
        self.connect_to_thickness( self.__thickness_update__ )

    def setName( self , name ):
        self.WRight.setName( name )

    def name( self ):
        return self.WRight.name()

    def setMethod( self , index ):
        return self.WRight.setMethod( index )

    def method( self ):
        return self.WRight.setMethod( index )

    def setThickness( self , thickness ):
        self.WRight.setThickness( thickness )

    def thickness( self )
        self.WRight.thickness()

