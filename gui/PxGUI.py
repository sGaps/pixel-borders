# Module:      gui.PxGUI.py | [ Language Python ]
# Created by: ( Gaps | sGaps | ArtGaps )
# -----------------------------------------------
# PyQt5 Modules:
from PyQt5.QtWidgets import QDialog , QWidget , QHBoxLayout , QVBoxLayout , QLayout

# Elements of the GUI:
from .Colors            import ColorButtons
from .AdvancedSettings  import AdvancedSettings
from .BasicSettings     import BasicSettings , INDEX_TYPES , TYPES , CUSTOM_INDEX
from .CloseButtons      import CloseButtons

# Krita dependent:
from .krita_connection.Lookup import KRITA_AVAILABLE
if KRITA_AVAILABLE:
    from .krita_connection.TimeOptions          import TimeOptions
    from .krita_connection.TransparencySettings import TransparencySettings
    from .krita_connection.Lookup               import kis , doc , node
    from .krita_connection.SpinBox              import SpinBoxFactory

# Defines a base class for the window ::::::::::::::::::::::::::::::
class DialogBox( QDialog ):
    def __init__( self , parent = None ): super().__init__( parent )
    def closeEvent( self , event ):       event.accept()


# Gui itself :::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
class GUI( object ):
    FG_DESC = ("FG",None)
    BG_DESC = ("BG",None)
    CS_DESC = ("CS",None)

    def __init__( self , parent = None , title = "PxGUI" ):
        self.window = DialogBox( parent )
        self.Lbody  = QVBoxLayout()
        self.window.setWindowTitle( title )
        # Do nothing
        self.borderizer = None

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
        #self.advanced.firstMethodChanged.connect(
        #        self.__preview_update_request__ )
        self.advanced.cellBeingEdited.connect(
                self.__preview_update_request__ )

        # Close actions setup:
        self.close.accept.connect( self.on_accept )
        self.close.cancel.connect( self.on_cancel )

        self.tryKonnect()

    def tryKonnect( self ):
        if KRITA_AVAILABLE:
            self.LKrita = QHBoxLayout()
            self.WKrita = QWidget()
            self.WKrita.setLayout( self.LKrita )

            index     = self.Lbody.indexOf( self.close )
            self.Lbody.insertWidget( index , self.WKrita )

            # [?] Time Options:
            self.time = TimeOptions()
            self.LKrita.addWidget( self.time )

            # Make connections:
            self.__on_enable_animation_update_request__( True )
            self.time.enabledAnimation.connect( self.__on_enable_animation_update_request__ )

            self.time.startTimeChanged.connect( self.__on_start_animation_update_request__ )
            self.time.endTimeChanged.connect  ( self.__on_end_animation_update_request__ )

            # [!] Transparency Options:
            self.transparency = TransparencySettings()
            index             = self.Lbody.indexOf( self.close )
            self.LKrita.addWidget( self.transparency )

            # Make connections:
            self.transparency.transparencyChanged.connect(
                    self.__on_transparency_update_request__ )

            self.transparency.thresholdChanged.connect(
                    self.__on_threshold_update_request__ )

            # [C] Color - Extra Options:
            self.color.tryCustomBuild( node , SpinBoxFactory )
            self.color.cs_released.connect( self.on_cs_release )

            self.data["node"] = node
            self.data["doc"]  = doc
            self.data["kis"]  = kis

    # Used as pyqtSlot( [int] , [float] )
    def __on_transparency_update_request__( self , value ):
        self.data["trdesc"][0] = value

    # Used as pyqtSlot( [int] , [float] )
    def __on_threshold_update_request__( self , value ):
        self.data["trdesc"][1] = value

    # Used as pyqtSlot( int )
    def __on_start_animation_update_request__( self , time ):
        self.data["animation"][0] = time

    # Used as pyqtSlot( int )
    def __on_end_animation_update_request__( self , time ):
        self.data["animation"][1] = time

    # Used as pyqtSlot( bool )
    def __on_enable_animation_update_request__( self , enabled ):
        if enabled:
            self.data["animation"] = self.time.getTime()
        else:
            self.data["animation"] = None

    # Works like a pyqtSlot( str ) 
    # Works like a pyqtSlot( int , int ) 
    def __preview_update_request__( self , row , col ):
        if col == 0:
            if self.dynPrev:
                self.settings.setIconByName( self.advanced.getCellContent(row,col) )
            else:
                self.settings.setIconByName( CUSTOM_INDEX )

    def on_type_update( self ):
        stype = self.settings.type()
        # Toogle advanced-buttons visibility:
        if stype == TYPES["simple"]:
            self.settings.setIconByName( self.advanced.getCellContent(0,0) )
            self.advanced.discardAllExceptFirst()
            self.advanced.hide_buttons()
            self.dynPrev = True
        elif stype == TYPES["custom"]:
            self.settings.setIconByName( CUSTOM_INDEX )
            self.advanced.show_buttons()
            self.dynPrev = False

    # Used as pyqtSlot()
    def on_cs_release( self ):
        self.data["colordsc"] = GUI.CS_DESC

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
        self.data["colordsc"]  = (self.data["colordsc"][0] , self.color.getComponents())

        self.report_data()
        if self.borderizer:
            self.borderizer.run( **self.data )
        # This closes the window
        self.window.accept()

    # Used as pyqtSlot()
    def on_cancel( self ):
        # This closes the window
        self.window.reject()

    def build_data( self ):
        """ builds the internal data used for in the widget.
            NOTE: GUI object isn't a QObject instance, so it cannot have explicit pyqtSignals and
                  pyqtSlots """
        self.data = {
                "methoddsc" : []          , # [[method,thickness]]
                "colordsc"  : GUI.FG_DESC , # ( color_type , components )
                "trdesc"    : [0,0]       , # Transparency descriptor = ( transparency_value , threshold )
                "name"      : "Border"    , # String
                # Attributes that requires a connection with krita:
                "node"      : None        , # Krita Node
                "doc"       : None        , # Krita Document
                "kis"       : None        , # Krita Instance
                "animation" : None          # None if it hasn't animation. Else [ start , finish ] -> start , finish are Ints in [UInt]
              }

    def report_data( self ):
        print( "Data Sent: {" )
        for k , v in self.data.items():
            print( f"{' ':4}{k}: {v}" )
        print( "}" )

    def setup_borderizer_connection( self , borderizer ):
        """ borderizer :: dict -> IO () """
        self.borderizer = borderizer

    def run( self ):
        self.window.show()
        self.window.activateWindow()

if __name__ == "__main__":
    gui = GUI(500,300)
    gui.setup()
