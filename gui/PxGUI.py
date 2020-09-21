# Module:      gui.PxGUI.py | [ Language Python ]
# Created by: ( Gaps | sGaps | ArtGaps )
# -----------------------------------------------
# PyQt5 Modules:
from PyQt5.QtWidgets import QDialog  , QVBoxLayout , QLayout

# Elements of the GUI:
from .Colors            import ColorButtons
from .AdvancedSettings  import AdvancedSettings
from .BasicSettings     import BasicSettings , INDEX_TYPES , TYPES
from .CloseButtons      import CloseButtons

# Defines a base class for the window ::::::::::::::::::::::::::::::
class DialogBox( QDialog ):
    def __init__( self , parent = None ): super().__init__( parent )
    def closeEvent( self , event ):       event.accept()


# Gui itself :::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
class GUI( object ):
    # TODO: add a borderizer parameter here:
    def __init__( self , parent = None , title = "PxGUI" ):
        self.window = DialogBox( parent )
        self.window.setWindowTitle( title )
        self.Lbody  = QVBoxLayout()
        # This is used for know when is displayed the optional data
        self.displayingExtra = True


        self.settings = BasicSettings   ()
        self.color    = ColorButtons    ()
        self.advanced = AdvancedSettings()
        self.close    = CloseButtons    ()

        self.build_data()

        # Main body building:
        self.Lbody.addWidget( self.settings )
        self.Lbody.addWidget( self.color    )
        self.Lbody.addWidget( self.advanced )
        self.Lbody.addWidget( self.close    )

        self.window.setLayout( self.Lbody )
        # This solves the resize problem It had before
        self.Lbody.setSizeConstraint( QLayout.SetFixedSize )

        # Aditional config:
        #self.advanced.setMaxOptionalValue(0)
        #self.toggle_optional_visibility()

        # Settings setup:
        self.settings.typeChanged.connect( self.on_type_update )
        self.settings.nameChanged.connect( self.on_name_update )

        # Color setup
        self.color.fg_released.connect( self.on_fg_release )
        self.color.bg_released.connect( self.on_bg_release )

        self.close.accept.connect( self.on_accept )
        self.close.cancel.connect( self.on_cancel )

        # TODO: REFACTOR
        # Signal conections:
        # self.settings..connect   ( self.on_method_update    )
        # self.settings.thicknessChanged.connect( self.on_thickness_update )

        # self.settings.methodChanged.connect( self.advanced.setOptionalDescription )

        # self.color.fg_released.connect( self.on_fg_release )
        # self.color.bg_released.connect( self.on_bg_release )


        # self.advanced.optionalChanged.connect( self.on_optional_update )

    def on_type_update( self ):
        stype = self.settings.type()
        if stype == TYPES["simple"]:
            self.advanced.discardAllExceptFirst()
            self.advanced.hide_butons()
        elif stype == TYPES["custom"]:
            self.advanced.show_butons()

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

    # Used as pyqtSlot( int )
    def on_thickness_update( self , thickness ):
        if self.data["thickness"] != thickness:
            self.data["thickness"] = thickness
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
        # Light update:
        self.data["methoddsc"] = self.advanced.getData()

        self.report_data()
        # This closes the window
        self.window.accept()

    # Used as pyqtSlot()
    def on_cancel( self ):
        # This closes the window
        self.window.reject()


    # TODO: Add "start" , "finish" , "custom-range" attributes.
    # TODO: add a new color "CS" -> Custom. Also add a new attribute "color-comp"
    def build_data( self ):
        """
        self.data = { "method"    : 0        ,  # METHOD[0]                == Classic
                      "thickness" : 1        ,  # Border Width / thickness == 1
                      "color"     : "FG"     ,  # Foreground Color
                      "name"      : "border" ,  # Layer name
                      "has-extra" : False    ,  # No more arguments
                      "extra-arg" : 0        ,  # value (For this case is dummy a value)
                      "start"     : -1       ,  # Start application frame on the timeline
                      "finish"    : -1       }  # Finish application frame on the timeline
                      """
        self.data = {
                "methoddsc" : []          , # [(method,thickness)]
                "colordsc"  : ("FG",None) , # ( color_type , components )
                "trdesc"    : None        , # Transparency descriptor = ( transparency_value , threshold )
                "name"      : "Border"    , # String
                # Attributes that requires a connection with krita:
                "node"      : None        , # Krita Node
                "doc"       : None        , # Krita Document
                "kis"       : None        , # Krita Instance
                "animation" : None          # None if it hasn't animation. Else ( start , finish ) -> start , finish are Ints in [UInt]
              }

    def report_data( self ):
        print( "Data Sent: {" )
        for k , v in self.data.items():
            print( f"{' ':4}{k}: {v}" )
        print( "}" )

    # TODO: Complete this after finish borders branch tasks
    def setup_borderizer_connection( self , borderizer ):
        pass

    def run( self ):
        self.window.show()
        self.window.activateWindow()


if __name__ == "__main__":
    gui = GUI(500,300)
    gui.setup()
