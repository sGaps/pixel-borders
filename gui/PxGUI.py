# Module:      gui.PxGUI.py | [ Language Python ]
# Created by: ( Gaps | sGaps | ArtGaps )
# -----------------------------------------------
"""
    Defines the GUI itself wich Holds all the information
    related to a border configuration.

    This 

    [:] Defined in this module
    --------------------------
    GUI :: class
        Main Window of the plugin. Represents a border configuration that
        can be edited by the user.

    [*] Created By 
     |- Gaps : sGaps : ArtGaps
"""



# PyQt5 Modules:
from PyQt5.QtWidgets import QDialog , QWidget , QMessageBox , QHBoxLayout , QVBoxLayout , QLayout

# Elements of the GUI:
from .Colors            import ColorButtons
from .AdvancedSettings  import AdvancedSettings
from .BasicSettings     import BasicSettings , INDEX_TYPES , TYPES , CUSTOM_INDEX
from .CloseButtons      import CloseButtons
from .DataLoader        import DataLoader
from sys                import stderr

# Misc.
import cProfile

# Krita dependent:
from .krita_connection.Lookup import KRITA_AVAILABLE
if KRITA_AVAILABLE:
    from .krita_connection.TimeOptions          import TimeOptions
    from .krita_connection.TransparencySettings import TransparencySettings
    from .krita_connection.Lookup               import kis
    from .krita_connection.SpinBox              import SpinBoxFactory

# Defines a base class for the window ::::::::::::::::::::::::::::::
class DialogBox( QDialog ):
    def __init__( self , parent = None ): super().__init__( parent )
    def closeEvent( self , event ):       event.accept()

# Gui itself :::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
# TODO: Add an warning when krita has an unsaved document
class GUI( object ):
    """
        Graphic User Interface of the Plugin.
    """
    FG_DESC = ["FG",None]
    BG_DESC = ["BG",None]
    CS_DESC = ["CS",None]
    
    def __init__( self , parent = None , title = "PxGUI" , profiler = False ):
        """
            ARGUMENTS
                parent(QWidget)
                title(str)
                profiler(bool)
            Builds all elements required to display the GUI and try to stablish
            a connection with Krita.
        """
        self.window = DialogBox( parent )
        self.Lbody  = QVBoxLayout()
        self.window.setWindowTitle( title )

        # Don't connect at begining
        self.borderizer = None
        # Does it require profiler?
        self.profiler   = profiler
        self.loader     = DataLoader()

        self.settings = BasicSettings   ()
        self.color    = ColorButtons    ()
        self.advanced = AdvancedSettings()
        self.close    = CloseButtons    ()
        self.dynPrev  = True            # Enables dynamic preview.

        self.data     = self.build_data()

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
        self.settings.loadRequest.connect( self.load_last_data )

        # Color setup:
        self.color.fg_released.connect( self.on_fg_release )
        self.color.bg_released.connect( self.on_bg_release )

        # Advanced setup:
        self.advanced.hide_buttons()
        self.advanced.cellBeingEdited.connect(
                self.__preview_update_request__ )

        # Close actions setup:
        self.close.accept.connect( self.on_accept )
        self.close.cancel.connect( self.on_cancel )

        self.tryKonnect()
        self.__preview_update_request__( 0 , 0 )

    def unsaved_document_warning( self ):
        """
            Display a warning when There isn't any document.
            for the canvas.
        """
        if KRITA_AVAILABLE and self.data["doc"]:
            doc = self.data["doc"]
            if not doc.fileName():
                self.time.setChecked( False )
                self.time.setEnabled( False )
                QMessageBox.information( self.window , "Warning: unsaved document" , 
                    "Unsaved document detected. please, save\n" +
                    "your document and open again the plugin\n" +
                    "to use the animation options." )

    def tryKonnect( self ):
        """
            Try to load each widget that depends on krita.
        """
        if KRITA_AVAILABLE:
            # [D] Data:
            doc  = kis.activeDocument()
            node = doc.activeNode() if doc else None
            self.data["node"] = node
            self.data["doc"]  = doc
            self.data["kis"]  = kis

            if not (kis and doc and node):
                return

            # [L] Layout & Extra Widgets:
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
        """ Actions performed when the accept button has been pressed. """
        self.close.setEnabled( False )
        # Light update:
        self.data["methoddsc"]   = self.advanced.getData()
        components               = self.color.getNormalizedComponents()
        self.data["colordsc"][1] = components

        self.report_data()
        if self.borderizer:
            # TODO: Move this to a different thread:
            if self.profiler:
                cProfile.runctx( "self.borderizer.run( **self.data )" , globals() , locals() )
            else:
                self.borderizer.run( **self.data )
        # This close and exit
        if KRITA_AVAILABLE:
            self.write_current_data()
        self.window.accept()

    # Used as pyqtSlot()
    def on_cancel( self ):
        """ Actions performed when press cancel button. """
        # This closes the window
        self.close.setEnabled( False )
        self.window.reject()


    def load_last_data( self ):
        """ Loads the previous configuration.
            (Only method description and name)"""
        retrieved = self.loader.loadData()
        if retrieved:
            self.data.update( retrieved )

            # Basic Settings:
            self.settings.setName( self.data["name"] )
            self.settings.setName( self.data["name"] )

            # This assumes a recipe is simple if it has only an element. Else is custom.
            if len(retrieved["methoddsc"]) > 1:
                self.settings.setTypeByName( "custom" )
            else:
                self.settings.setTypeByName( "simple" )
            self.advanced.setRecipe( self.data["methoddsc"] )

            # TODO: Is this totally right, I mean... This uses an argument that depends
            #       on the color space.
            if KRITA_AVAILABLE:
                tr , th = retrieved["trdesc"]
                self.transparency.setTransparency( tr )
                self.transparency.setThreshold( th )

    def write_current_data( self ):
        """ Write the current data contents into a .json file """
        toWrite = self.data.copy()
        toWrite.pop( "node" )
        toWrite.pop( "doc" )
        toWrite.pop( "kis" )
        toWrite.pop( "colordsc" )
        toWrite.pop( "animation" )
        toWrite.pop( "trdesc" )
        self.loader.writeData( toWrite )

    def build_data( self ):
        """ 
            RETURNS
                dict
            builds the internal shared data.
        """
        data = {
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

        return data

    def report_data( self ):
        """
            IO-ACTION
                print on stderr the shared data.
        """
        print( "[PxGUI] Data Sent: {" , file = stderr )
        for k , v in self.data.items():
            print( f"{' ':4}{k}: {v}" , file = stderr )
        print( "}" , file = stderr )

    def setup_borderizer_connection( self , borderizer ):
        """
            ARGUMENTS
                borderizer(core.Borderizer.Borderizer): Object that makes the true border using the core's modules
            Sets the borderizer object.
        """
        self.borderizer = borderizer

    def run( self ):
        """
            Setup everything execute the GUI.
        """
        self.window.show()
        self.window.activateWindow()
        self.unsaved_document_warning()
