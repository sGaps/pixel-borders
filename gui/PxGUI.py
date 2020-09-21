# Module:      gui.PxGUI.py | [ Language Python ]
# Created by: ( Gaps | sGaps | ArtGaps )
# -----------------------------------------------
# PyQt5 Modules:
from PyQt5.QtWidgets import QDialog , QVBoxLayout , QLayout

# Elements of the GUI:
from .Colors            import ColorButtons
from .AdvancedSettings  import AdvancedSettings
from .BasicSettings     import BasicSettings , INDEX_TYPES , TYPES , CUSTOM_INDEX
from .CloseButtons      import CloseButtons

# Defines a base class for the window ::::::::::::::::::::::::::::::
class DialogBox( QDialog ):
    def __init__( self , parent = None ): super().__init__( parent )
    def closeEvent( self , event ):       event.accept()


# Gui itself :::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
class GUI( object ):
    FG_DESC = ("FG",None)
    BG_DESC = ("BG",None)
    # TODO: add a borderizer parameter here:
    # TODO: Connect Preview/Settings with first parameter of AdvancedSettings, so it would show an icon
    #       related to the current method.
    def __init__( self , parent = None , title = "PxGUI" ):
        self.window = DialogBox( parent )
        self.Lbody  = QVBoxLayout()
        self.window.setWindowTitle( title )

        self.settings = BasicSettings   ()
        self.color    = ColorButtons    ()
        self.advanced = AdvancedSettings()
        self.close    = CloseButtons    ()
        self.dynPrev  = True            # Enables dynamic preview.

        self.build_data()

        # Main body building:
        self.Lbody.addWidget( self.settings )
        self.Lbody.addWidget( self.color    )
        self.Lbody.addWidget( self.advanced )
        self.Lbody.addWidget( self.close    )

        self.window.setLayout( self.Lbody )
        # This solves the resize problem It had before
        self.Lbody.setSizeConstraint( QLayout.SetFixedSize )

        # Settings setup:
        self.settings.typeChanged.connect( self.on_type_update )
        self.settings.nameChanged.connect( self.on_name_update )

        # Color setup:
        self.color.fg_released.connect( self.on_fg_release )
        self.color.bg_released.connect( self.on_bg_release )

        # Advanced setup:
        self.advanced.hide_buttons()
        self.advanced.firstMethodChanged.connect(
                self.__preview_update_request__ )

        # Close actions setup:
        self.close.accept.connect( self.on_accept )
        self.close.cancel.connect( self.on_cancel )

    # Works like a pyqtSlot( str ) 
    def __preview_update_request__( self , method ):
        if self.dynPrev:
            self.settings.setIconByName( method )
        else:
            self.settings.setIconByName( CUSTOM_INDEX )

    def on_type_update( self ):
        stype = self.settings.type()
        # Toogle advanced-buttons visibility:
        if stype == TYPES["simple"]:
            self.advanced.discardAllExceptFirst()
            self.advanced.hide_buttons()
            self.dynPrev = True
        elif stype == TYPES["custom"]:
            self.advanced.show_buttons()
            self.dynPrev = False

    def hasExtra( self ):
        return self.data["method"] > 1

    # Used as pyqtSlot( str )
    def on_name_update( self , name ):
        self.data["name"] = name

    # Used as pyqtSlot()
    def on_fg_release( self ):
        self.data["colordsc"] = GUI.FG_DESC

    # Used as pyqtSlot( int )
    def on_bg_release( self ):
        self.data["colordsc"] = GUI.BG_DESC

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
        """ builds the internal data used for in the widget.
            NOTE: GUI object isn't a QObject instance, so it cannot have explicit pyqtSignals and
                  pyqtSlots """
        self.data = {
                "methoddsc" : []          , # [[method,thickness]]
                "colordsc"  : GUI.FG_DESC , # ( color_type , components )
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
