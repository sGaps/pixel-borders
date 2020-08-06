# Module:      gui.PxGUI.py | [ Language Python ]
# Created by: ( Gaps | sGaps | ArtGaps )
# -----------------------------------------------
# PyQt5 Modules:
from PyQt5.QtWidgets import QDialog  , QVBoxLayout 

# Elements of the GUI:
from .Colors         import ColorButtons
from .Advanced       import AdvancedSettings
from .Settings       import SettingsDisplay
from .CloseButtons   import CloseButtons

# Body class for the window ::::::::::::::::::::::::::::::::::::::::
class DialogBox( QDialog ):
    def __init__( self , parent = None ): super().__init__( parent )
    def closeEvent( self , event ):       event.accept()


# TODO: See if is actually necessary change the parent class by a QObject/QWidget class
# Gui itself :::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
class GUI( object ):
    # TODO: add a borderizer parameter here:
    def __init__( self , width , height , parent = None , title = "PxGUI" ):
        self.window = DialogBox( parent )
        self.window.setWindowTitle( title )
        self.Lbody  = QVBoxLayout()
        self.displayingExtra = True

        PROPORTIONS = { "settings" : (width,height) ,
                        "color"    : (width,height) ,
                        "advanced" : (width,height) ,
                        "close"    : (width,height) }

        self.settings = SettingsDisplay ( *PROPORTIONS["settings"] )
        self.color    = ColorButtons    ( *PROPORTIONS["color"]    )
        self.advanced = AdvancedSettings( *PROPORTIONS["advanced"] )
        self.close    = CloseButtons    ( *PROPORTIONS["close"]    )

        self.build_data()
        self.__setup_size__( width , height )

        # Main body building:
        self.Lbody.addWidget( self.settings )
        self.Lbody.addWidget( self.color    )
        self.Lbody.addWidget( self.advanced )
        self.Lbody.addWidget( self.close    )

        self.window.setLayout( self.Lbody )

        # Aditional config:
        self.advanced.setMaxOptionalValue(0)
        self.toggle_optional_visibility()

        # Signal conections:
        self.settings.methodChanged.connect   ( self.on_method_update    )
        self.settings.nameChanged.connect     ( self.on_name_update      )
        self.settings.thicknessChanged.connect( self.on_thickness_update )

        self.settings.methodChanged.connect( self.advanced.setOptionalDescription )

        self.color.fg_released.connect( self.on_fg_release )
        self.color.bg_released.connect( self.on_bg_release )

        self.close.accept.connect( self.on_accept )
        self.close.cancel.connect( self.on_cancel )

        self.advanced.optionalChanged.connect( self.on_optional_update )

    def hasExtra( self ):
        return self.data["method"] > 1

    # They cannot be Slots because this isn't a QObject
    # Used as pyqtSlot( int )
    def on_method_update( self , index_method ):
        self.data["method"]    = index_method
        self.data["has-extra"] = self.hasExtra()
        self.toggle_optional_visibility()

    def toggle_optional_visibility( self ):
        if self.data["has-extra"]:
            if not self.displayingExtra:
                self.advanced.show_all()
                self.displayingExtra = True
        else:
            if self.displayingExtra:
                self.advanced.hide_all()
                self.displayingExtra = False


    # Used as pyqtSlot( str )
    def on_name_update( self , name ):
        self.data["name"] = name

    # TODO: Observe this method
    # Used as pyqtSlot( int )
    def on_thickness_update( self , thickness ):
        if self.data["thickness"] != thickness:
            self.data["thickness"] = thickness
            # This only sets a new limit but doesn't bind the method itself
            self.advanced.setMaxOptionalValue( thickness - 1 )

    # Used as pyqtSlot()
    def on_fg_release( self ):
        self.data["color"] = "FG"

    # Used as pyqtSlot( int )
    def on_bg_release( self ):
        self.data["color"] = "BG"


    # Used as pyqtSlot( int )
    def on_optional_update( self , value ):
        if self.data["extra-arg"] != value:
            self.data["extra-arg"] = value

    # Used as pyqtSlot()
    def on_accept( self ):
        self.report_data()
        pass

    # Used as pyqtSlot()
    def on_cancel( self ):
        pass


    def __setup_size__( self , width , height ):
        pass

    # TODO: Add "start" , "finish" , "custom-range" attributes.
    # TODO: add a new color "CS" -> Custom. Also add a new attribute "color-comp"
    def build_data( self ):
        self.data = { "method"    : 0        ,  # METHOD[0]                == Classic
                      "thickness" : 1        ,  # Border Width / thickness == 1
                      "color"     : "FG"     ,  # Foreground Color
                      "name"      : "border" ,  # Layer name
                      "has-extra" : False    ,  # No more arguments
                      "extra-arg" : 0        ,  # value (For this case is dummy a value)
                      "start"     : -1       ,  # Start application frame on the timeline
                      "finish"    : -1       }  # Finish application frame on the timeline

    def report_data( self ):
        print( "Data Sent: {" )
        for k , v in self.data.items():
            print( f"{' ':4}{k}: {v}" )
        print( "}" )

    def setup_borderizer_connection( self , borderizer ):
        pass

    def run( self ):
        #self.setup_connections()
        #self.setup_size_constraints()
        #self.__adjust_components__()
        self.window.show()
        self.window.activateWindow()


if __name__ == "__main__":
    gui = GUI(500,300)
    gui.setup()
