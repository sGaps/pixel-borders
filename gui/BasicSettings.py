# Module:      gui.Settings.py | [ Language Python ]
# Created by: ( Gaps | sGaps | ArtGaps )
# --------------------------------------------------
from PyQt5.QtWidgets import ( QComboBox   , QLineEdit   , QSpinBox     , QGroupBox , QWidget ,  # Widgets 
                              QVBoxLayout , QHBoxLayout , QFormLayout  , QLabel )               # Layouts
from PyQt5.Qt        import Qt                                              # Constants
from .Preview        import Preview , CUSTOM_INDEX , ICON_NUMBER , TABLE    # Icon/Image handle
from PyQt5.QtCore    import pyqtSlot , pyqtSignal

class ImageDisplay( QGroupBox ):
    """ Contains and show a image
        SIGNALS:
            void imageChanged( int )
        SLOTS:
            void select_image( int )
            void load_image_from( str )
    """
    imageChanged = pyqtSignal( int )

    def __init__( self , parent = None ):
        super().__init__( parent )
        self.Lmain = QVBoxLayout()
        self.image = Preview()
        self.index = -1
        self.Lmain.addWidget( self.image )

        self.setTitle( "Preview" )
        self.setLayout( self.Lmain )

    @pyqtSlot( int )
    def select_image( self , index ):
        self.image.setIconFromIndex( index )
        self.index = index
        self.imageChanged.emit( index )

    @pyqtSlot( str )
    def select_image_by_name( self , method_name ):
        self.select_image( TABLE.get( method_name , CUSTOM_INDEX ) )

    @pyqtSlot( str )
    def load_image_from( self , relative_path ):
        self.image.loadImg( relative_path )
        self.index = -1
        self.imageChanged.emit( -1 )

    def getImageIndex( self ):
        return self.index

MAXNAMELENGTH = 64 
EDITNAMEMODE  = QLineEdit.Normal

TYPES       = { "simple" : 0 , "custom" : 1 }
DESCRIPTION = { -1 : "No description." , 0 : "Quick way to make borders." , 1 : "Build your own borders." }
INDEX_TYPES = { 0 : "simple" , 1 : "custom" }

class BasicInfo( QGroupBox ):
    """ Retrieve basic information about the border.
        SIGNALS:
            void typeChanged( int )
            void nameChanged( str )
        SLOTS:
            void setName( str )         => emits a nameChanged signal
            void setType( int )         => emits a typeChanged signal
            void setTypeByName( str )   => emits a typeChanged signal
    """
    typeChanged = pyqtSignal( int )
    nameChanged = pyqtSignal( str )

    def __init__( self , parent = None ):
        super().__init__( parent )
        self.Lmain = QFormLayout()
        self.Wname = QLineEdit()
        self.Wtype = QComboBox()
        self.Wdesc = QLabel()

        self.Wname.setMaxLength( 64 )
        self.Wname.setEchoMode ( QLineEdit.Normal )

        self.Wtype.setInsertPolicy    ( QComboBox.InsertAtBottom   )
        self.Wtype.setSizeAdjustPolicy( QComboBox.AdjustToContents )
        self.Wtype.addItems           ( TYPES.keys()               )
        self.Wtype.setCurrentIndex    ( 0                          )
        self.Wdesc.setText( DESCRIPTION[0] )

        self.Lmain.setLabelAlignment( Qt.AlignLeft | Qt.AlignVCenter )

        self.Lmain.addRow( "Recipe type"    , self.Wtype )
        self.Lmain.addRow( "Layer Name"     , self.Wname )
        self.Lmain.addRow( self.Wdesc )

        self.setTitle( "Basic Settings" )
        self.setLayout( self.Lmain )

        self.Wname.textChanged.connect( self.__update_name_request__ )
        self.Wtype.currentIndexChanged.connect( self.__update_type_request__ )
        self.typeChanged.connect( self.__update_desc_request )

    @pyqtSlot( int )
    def __update_desc_request( self , index ):
        self.Wdesc.setText( DESCRIPTION.get(index,-1) )
    @pyqtSlot( str )
    def __update_name_request__( self , name ):
        self.nameChanged.emit( name )

    @pyqtSlot( int )
    def __update_thickness_request__( self , thickness ):
        self.thicknessChanged.emit( thickness )

    @pyqtSlot( int )
    def __update_type_request__( self , index ):
        self.typeChanged.emit( index )

    @pyqtSlot( str )
    def setName( self , name ):
        if self.name() != name:
            self.Wname.setText( name )
            self.nameChanged.emit( name )

    def name( self ):
        return self.Wname.text()

    @pyqtSlot( int )
    def setType( self , index ):
        """ defines the the current border type """
        if index in DESCRIPTION and self.type() != index:
            self.Wtype.setCurrentIndex( index )
            self.typeChanged.emit( index )

    @pyqtSlot( str )
    def setTypeByName( self , typename ):
        if typename in TYPES:
            self.setType( TYPES[typename] )

    def type( self ):
        return self.Wtype.currentIndex()

    def typeByName( self ):
        return INDEX_TYPES[ self.typeByName() ]
    
class BasicSettings( QWidget ):
    """ Retrieve information about the method and display an image.
        SIGNALS:
            void iconChanged( int )
            void typeChanged( int )
            void nameChanged( str )
        SLOTS:
            void setIcon( int )         => emits a imageChanged signal
            void setIconByName( int )   => emits a imageChanged signal
            void setName( str )         => emits a nameChanged signal
            void setType( int )         => emits a typeChanged signal
            void setTypeByName( str )   => emits a typeChanged signal
    """
    typeChanged = pyqtSignal( int )
    iconChanged = pyqtSignal( int )
    nameChanged = pyqtSignal( str )
    def __init__( self , parent = None ):
        super().__init__( parent )
        self.Lmain  = QHBoxLayout ()
        self.WLeft  = ImageDisplay()
        self.WRight = BasicInfo()

        self.Lmain.addWidget( self.WLeft  )
        self.Lmain.addWidget( self.WRight )
        self.Lmain.addStretch(1)
        self.WRight.setName( "border" )

        self.setLayout( self.Lmain )

        self.WRight.nameChanged.connect( self.__update_name_request__ )
        self.WRight.typeChanged.connect( self.__update_type_request__ )
        self.WLeft.imageChanged.connect( self.__update_icon_request__ )

    @pyqtSlot( str )
    def __update_name_request__( self , name ):
        self.nameChanged.emit( name )

    @pyqtSlot( int )
    def __update_type_request__( self , index ):
        self.typeChanged.emit( index )

    @pyqtSlot( int )
    def __update_icon_request__( self , index ):
        self.iconChanged.emit( index )

    @pyqtSlot( int )
    def setName( self , name ):
        if self.name() == name:
            self.WRight.setName( name )
            self.nameChanged.emit( name )

    def name( self ):
        return self.WRight.name()

    @pyqtSlot( int )
    def setType( self , index ):
        if self.method() == index:
            self.WRight.setType( index )
            self.typeChanged.emit( index )

    def type( self ):
        return self.WRight.type()

    @pyqtSlot( int )
    def setIcon( self , index ):
        if self.WLeft.getImageIndex() != index:
            self.WLeft.select_image( index )
            self.iconChanged.emit( index )

    @pyqtSlot( str )
    def setIconByName( self , method_name ):
        self.WLeft.select_image_by_name( method_name )

    def icon( int ):
        return self.WLeft.getImageIndex()

    @staticmethod
    def CustomIndex():
        return CUSTOM_INDEX

    @staticmethod
    def AvailableIconRange():
        return range(ICON_NUMBER)

