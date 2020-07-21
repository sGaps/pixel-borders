# Widget imports
from PyQt5.QtWidgets import ( QDialog , QLabel , QComboBox , QLineEdit , QSpinBox , QGroupBox , QPushButton , QDialogButtonBox )

# Layout imports
from PyQt5.QtWidgets import ( QVBoxLayout , QHBoxLayout , QFormLayout )

# Constants imports
from PyQt5.Qt        import Qt

# Local import:
from Image import Preview

# Body class for the window ----------------------------------------
class DialogBox( QDialog ):
    def __init__( self , parent = None ): super().__init__( parent )
    def closeEvent( self , event ):       event.accept()




# CONSTANTS #
METHODS = { 0 : "Classic" ,
            1 : "Corners" ,
            2 : "Classic then Corners" ,
            3 : "Corners then Classic" ,
            4 : "Classic with Corners" ,
            5 : "Corners with Classic" }

ADVDESC = { "sequential" : "Switch to second method application after" ,
            "combinated" : "Start to apply second method after"        ,
            "none"       : ""                                          }



# TODO: Make everything like a Widget Composition.
# TODO: Convert dict types into simple variables.
# NOTE: Use QGroupBox for this. Create Classes for manage your boxes
#       Like -> class Settings( QGroupBox ): ; def __init__(self): self.name , self.width , self.method ... ;
# See more on: https://doc.qt.io/qt-5/qtwidgets-widgets-groupbox-example.html
class GUI( object ):
    def __init__( self , width , height , parent = None ):
        # Basic attributes:
        self.width  = width
        self.height = height
        self.window = DialogBox( parent )

        self.build_data()
        self.build_basicSettings()
        self.build_colorSettings()
        self.build_advncSettings()
        self.build_closeWButtons()
        self.build_body()

    def build_data( self ):
        self.data = { "method"    : 0        ,  # METHOD[0]                == Classic
                      "width"     : 1        ,  # Border Width / thickness == 1
                      "color"     : "FG"     ,  # Foreground Color
                      "name"      : "border" ,  # Layer name
                      "has-extra" : False    ,  # No more arguments
                      "extra-arg" : 0        }  # value (For this case is dummy a value)


    def build_basicSettings( self ):
        self.layoutSettings = { "main" : QHBoxLayout() ,
                                "L"    : QVBoxLayout() ,
                                "R"    : QFormLayout() }

        # Widgets Declaration [Main objects]
        self.widgetSettings = { "method" : QComboBox() ,
                                "name"   : QLineEdit() ,
                                "width"  : QSpinBox()  ,
                                "LBody"  : QGroupBox() ,
                                "RBody"  : QGroupBox() }

        self.methodPreview  = Preview()

        # Widget Config [Left]
        self.layoutSettings["L"].addWidget( self.methodPreview )
        #self.methodPreview.setText( "Hello there" )
        self.methodPreview.setIconFromIndex( self.data["method"] )

        # Widget Config [Right]
        self.widgetSettings["method"].setInsertPolicy    ( QComboBox.InsertAtBottom   )
        self.widgetSettings["method"].setSizeAdjustPolicy( QComboBox.AdjustToContents )
        self.widgetSettings["method"].addItems           ( METHODS.values()           )
        self.widgetSettings["method"].setCurrentIndex    ( self.data["method"]        )

        self.widgetSettings["name"].setMaxLength( 64 )
        self.widgetSettings["name"].setEchoMode ( QLineEdit.Normal  )
        self.widgetSettings["name"].setText     ( self.data["name"] )

        self.widgetSettings["width"].setMinimum  ( 1   )
        self.widgetSettings["width"].setMaximum  ( 200 )
        self.widgetSettings["width"].setSuffix   ( "px"          )
        self.widgetSettings["width"].setAlignment( Qt.AlignRight )
        
        # Adding Widgets into layouts:
        self.layoutSettings["R"].addRow( "Method"         , self.widgetSettings["method"] )
        self.layoutSettings["R"].addRow( "Layer Name"     , self.widgetSettings["name"]   )
        self.layoutSettings["R"].addRow( "Line thickness" , self.widgetSettings["width"]  )

        # Adding Layouts to [QGroupBox(es) <==]:
        self.widgetSettings["LBody"].setLayout( self.layoutSettings["L"] )
        self.widgetSettings["RBody"].setLayout( self.layoutSettings["R"] )
        self.widgetSettings["LBody"].setTitle( "Preview"  )
        self.widgetSettings["RBody"].setTitle( "Settings" )

        # WORKS!
        self.layoutSettings["main"].addWidget( self.widgetSettings["LBody"] )
        self.layoutSettings["main"].addWidget( self.widgetSettings["RBody"] )
        self.layoutSettings["main"].addStretch(1)

    def build_colorSettings( self ):
        # TODO: Put QButtonGroup here for manage FG & BG buttons (make them exclusives)
        self.layoutColor = QHBoxLayout()
        self.widgetColor = { "FG"   : QPushButton( "Foreground" ) ,
                             "BG"   : QPushButton( "Background" ) ,
                             "main" : QGroupBox()                 }

        self.layoutColor.addWidget( self.widgetColor["FG"] )
        self.layoutColor.addWidget( self.widgetColor["BG"] )
        self.layoutColor.addStretch(1)

        self.widgetColor["FG"].setCheckable( True  )
        self.widgetColor["FG"].setChecked  ( True  )

        self.widgetColor["BG"].setCheckable( True  )
        self.widgetColor["BG"].setChecked  ( False )

        self.widgetColor["main"].setLayout( self.layoutColor )
        self.widgetColor["main"].setTitle ( "Color Settings" )

    def build_advncSettings( self ):
        # TODO Define this as QGridLayout() for avoid ["arg"] weird translation after ["desc"] update
        self.layoutAdvnc = { "main" : QFormLayout() }
        self.widgetAdvnc = { "arg"  : QSpinBox()    ,
                             "desc" : QLabel()      ,
                             "main" : QGroupBox()   }

        self.widgetAdvnc["arg"].setMinimum  ( 0 )
        self.widgetAdvnc["arg"].setMaximum  ( self.data["width"] - 1 )
        self.widgetAdvnc["arg"].setAlignment( Qt.AlignRight )
        self.widgetAdvnc["arg"].setMaximumWidth( 80 )

        self.widgetAdvnc["desc"].setText( self.getDesc() )

        self.widgetAdvnc["main"].setLayout( self.layoutAdvnc["main"]                           )
        self.layoutAdvnc["main"].addRow   ( self.widgetAdvnc["desc"] , self.widgetAdvnc["arg"] )
        self.widgetAdvnc["main"].setTitle ( "Advanced Options" )

        self.__update_adv_visibility__()

    def build_closeWButtons( self ):
        self.layoutClose = QHBoxLayout()
        self.widgetClose = { "buttons" : QDialogButtonBox( QDialogButtonBox.Ok 
                                                         | QDialogButtonBox.Cancel ) }

        self.layoutClose.addStretch(1)
        self.layoutClose.addWidget( self.widgetClose["buttons"] )

    def build_body( self ):
        self.layoutBody = QVBoxLayout()

        self.layoutBody.addLayout( self.layoutSettings["main"] )
        self.layoutBody.addWidget( self.widgetColor["main"]    )
        self.layoutBody.addWidget( self.widgetAdvnc["main"]    )
        self.layoutBody.addLayout( self.layoutClose            )

        # Final Building up:
        self.window.setLayout( self.layoutBody )

    # TODO: Add more configuration
    def __adjust_components__( self ):
        self.window.resize( self.width , self.height )

    def getDesc( self ):
        m = self.data["method"]
        if   m < 2: return ADVDESC["none"]
        elif m < 4: return ADVDESC["sequential"]
        elif m < 6: return ADVDESC["combinated"]
        else:       return ADVDESC["none"]

    def resize( self , width , height ):
        self.width  = width
        self.height = height
        self.__adjust_components__()

    def setup_connections( self ):
        self.settings_connect()
        self.colors_connect()
        self.closing_connect()
        self.advanced_connect()


    def __update__method_depends__( self ):
        index = self.widgetSettings["method"].currentIndex()
        self.data["method"] = index
        self.methodPreview.setIconFromIndex( index )
        self.__update_adv_visibility__()

    def __update_adv_visibility__( self ):
        index = self.data["method"]
        extra = self.data["has-extra"]
        if   index < 2:
            self.data["has-extra"] = False
            for widget in self.widgetAdvnc.values():
                widget.hide()
        else:
            if not self.data["has-extra"]:
                for widget in self.widgetAdvnc.values():
                    widget.show()
            self.data["has-extra"] = True
            self.widgetAdvnc["desc"].setText( self.getDesc() )

    def __update__name_depends__( self ):
        self.data["name"] = self.widgetSettings["name"].text()

    def __update__width_depends__( self ):
        self.data["width"] = self.widgetSettings["width"].value()
        self.widgetAdvnc["arg"].setMaximum( self.data["width"] - 1 )

    def __update__fg_depends__( self ):
        self.data["color"] = "FG"
        self.widgetColor["FG"].setChecked( True  )
        self.widgetColor["BG"].setChecked( False )

    def __update__bg_depends__( self ):
        self.data["color"] = "BG"
        self.widgetColor["BG"].setChecked( True  )
        self.widgetColor["FG"].setChecked( False )

    def settings_connect( self ):
        self.widgetSettings["method"].currentIndexChanged.connect( self.__update__method_depends__ )
        self.widgetSettings["name"].textChanged.connect          ( self.__update__name_depends__   )
        self.widgetSettings["width"].valueChanged.connect        ( self.__update__width_depends__  )

    # TODO: Finish
    def colors_connect( self ):
        self.widgetColor["FG"].released.connect( self.__update__fg_depends__ )
        self.widgetColor["BG"].released.connect( self.__update__bg_depends__ )

    def closing_connect( self ):
        self.widgetClose["buttons"].accepted.connect( self.call_borderizer )
        self.widgetClose["buttons"].rejected.connect( self.window.close    )

    def __update__advArg_depends__( self ):
        self.data["extra-arg"] = self.widgetAdvnc["arg"].value()

    def advanced_connect( self ):
        self.widgetAdvnc["arg"].valueChanged.connect( self.__update__advArg_depends__ )

    def report_data( self ):
        print( "Sending Data: {" )
        for k , v in self.data.items():
            print( k , ":" , v )
        print( "}" )

    def call_borderizer( self ):
        self.report_data()

    def run( self ):
        self.setup_connections()
        self.__adjust_components__()
        self.window.show()
        self.window.activateWindow()


if __name__ == "__main__":
    gui = GUI(500,300)
    gui.setup()
