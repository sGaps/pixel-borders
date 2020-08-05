# Module:      gui.PxGUI.py | [ Language Python ]
# Created by: ( Gaps | sGaps | ArtGaps )
# -----------------------------------------------
from PyQt5.QtWidgets import (   # Widgets :::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
                                QDialog     , QLabel      , QComboBox         , QLineEdit , QSpinBox  ,
                                QGroupBox   , QPushButton , QDialogButtonBox  ,
                                # Layouts ::::::::::::::::::::::::::::::::::::::::::::::::::::::
                                QVBoxLayout , QHBoxLayout , QFormLayout , QBoxLayout , QLayout )
from PyQt5.QtCore import pyqtSlot , pyqtSignal
# Elements of the GUI:
from .Colors        import ColorButtons
from .Advanced      import AdvancedSettings
from .Settings      import SettingsDisplay
from .CloseButtons  import CloseButtons

# Body class for the window ::::::::::::::::::::::::::::::::::::::::
class DialogBox( QDialog ):
    def __init__( self , parent = None ): super().__init__( parent )
    def closeEvent( self , event ):       event.accept()


# CONSTANTS ----------------------------
METHODS = { 0 : "Classic"              ,
            1 : "Corners"              ,
            2 : "Classic then Corners" ,
            3 : "Corners then Classic" ,
            4 : "Classic with Corners" ,
            5 : "Corners with Classic" }

ADVDESC = { "sequential" : "Switch to second method application after" ,
            "combinated" : "Start to apply second method after"        ,
            "none"       : ""                                          }

PROPORTION = { "settings" : (0.95,0.58) ,
               "colors"   : (0.95,0.25) ,
               "advanced" : (0.95,0.25) ,
               "close"    : (0.95,0.08) }

COLOR = { "FG" , "BG" , "CUSTOM" }

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

        self.settings = SettingsDisplay( *PROPORTIONS["settings"] )
        self.color    = ColorButtons( *PROPORTIONS["color"] )
        self.advanced = AdvancedSettings( *PROPORTIONS["advanced"] )
        self.close    = CloseButtons( *PROPORTIONS["close"] )

        self.build_data()
        self.__setup_size__( width , height )

        self.Lbody.addWidget( self.settings )
        self.Lbody.addWidget( self.color )
        self.Lbody.addWidget( self.advanced )
        self.Lbody.addWidget( self.close )

        self.window.setLayout( self.Lbody )


        self.advanced.setMaxOptionalValue(0)
        self.toggle_optional_visibility()
        self.settings.methodChanged.connect( self.on_method_update )
        self.settings.nameChanged.connect( self.on_name_update )
        self.settings.thicknessChanged.connect( self.on_thickness_update )

        self.settings.methodChanged.connect( self.advanced.setOptionalDescription )

        self.color.fg_released.connect( self.on_fg_release )
        self.color.bg_released.connect( self.on_bg_release )

        self.close.accept.connect( self.on_accept )
        self.close.cancel.connect( self.on_cancel )

    def hasExtra( self ):
        return self.data["method"] > 1

    # They cannot be Slots because this isn't a QObject
    #@pyqtSlot( int )
    def on_method_update( self , index_method ):
        self.data["method"]    = index_method
        self.data["has-extra"] = self.hasExtra()
        self.toggle_optional_visibility()

    # TODO: Fix visibility problem
    def toggle_optional_visibility( self ):
        if self.data["has-extra"]:
            if not self.displayingExtra:
                self.advanced.show_all()
                self.displayingExtra = True
        else:
            if self.displayingExtra:
                self.advanced.hide_all()
                self.displayingExtra = False


    #@pyqtSlot( str )
    def on_name_update( self , name ):
        self.data["name"] = name

    #@pyqtSlot( int )
    def on_thickness_update( self , thickness ):
        if self.data["thickness"] != thickness:
            self.data["method"] = thickness
            self.advanced.setMaxOptionalValue( thickness - 1 )

    #@pyqtSlot()
    def on_fg_release( self ):
        self.data["color"] = "FG"

    #@pyqtSlot()
    def on_bg_release( self ):
        self.data["color"] = "BG"


    #@pyqtSlot( int )
    def on_optional_update( self , value ):
        if self.data["extra-arg"] != value:
            self.data["extra-arg"] = value

    #@pyqtSlot()
    def on_accept( self ):
        self.report_data()
        pass

    def on_cancel( self ):
        pass


    def __setup_size__( self , width , height ):
        pass

    def build_data( self ):
        # TODO: Add "start" , "finish" , "custom-range" attributes.
        # TODO: add "custom"
        self.data = { "method"    : 0        ,  # METHOD[0]                == Classic
                      "thickness" : 1        ,  # Border Width / thickness == 1
                      "color"     : "FG"     ,  # Foreground Color
                      "name"      : "border" ,  # Layer name
                      "has-extra" : False    ,  # No more arguments
                      "extra-arg" : 0        ,  # value (For this case is dummy a value)
                      "start"     : -1       ,  # Start application frame on the timeline
                      "finish"    : -1       }  # Finish application frame on the timeline


    # DEPRECATED
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
        self.layoutSettings["R"].setLabelAlignment( Qt.AlignLeft | Qt.AlignVCenter )
        self.layoutSettings["R"].addRow( "Method"         , self.widgetSettings["method"] )
        self.layoutSettings["R"].addRow( "Layer Name"     , self.widgetSettings["name"]   )
        self.layoutSettings["R"].addRow( "Line thickness" , self.widgetSettings["width"]  )

        # Adding Layouts to [QGroupBox(es) <==]:
        self.widgetSettings["LBody"].setLayout( self.layoutSettings["L"] )
        self.widgetSettings["RBody"].setLayout( self.layoutSettings["R"] )
        self.widgetSettings["LBody"].setTitle( "Preview"  )
        self.widgetSettings["RBody"].setTitle( "Settings" )
        # SIZES LBODY -> (156,177) ; RBODY -> (270,140)

        # WORKS!
        self.layoutSettings["main"].addWidget( self.widgetSettings["LBody"] )
        self.layoutSettings["main"].addWidget( self.widgetSettings["RBody"] )
        self.layoutSettings["main"].addStretch(1)

    def build_colorSettings( self ):
        self.layoutColor = QHBoxLayout()
        self.widgetColor = { "FG"   : QPushButton( "Foreground" ) ,
                             "BG"   : QPushButton( "Background" ) ,
                             "main" : QGroupBox()                 }

        self.layoutColor.addWidget( self.widgetColor["FG"] )
        self.layoutColor.addWidget( self.widgetColor["BG"] )
        self.layoutColor.setSizeConstraint( QLayout.SetDefaultConstraint )

        # TODO: Search more info in: https://doc.qt.io/archives/qt-4.8///qabstractbutton.html#autoExclusive-prop
        # There, is the function: autoExclusive button, it looks useful for this.
        self.widgetColor["FG"].setCheckable( True  )
        self.widgetColor["FG"].setChecked  ( True  )

        self.widgetColor["BG"].setCheckable( True  )
        self.widgetColor["BG"].setChecked  ( False )

        self.widgetColor["main"].setLayout( self.layoutColor )
        self.widgetColor["main"].setTitle ( "Color Settings" )
        # SIZE MAIN -> (196,77)
        self.widgetColor["main"].setFixedHeight( 77 )

    def build_advncSettings( self ):
        self.layoutAdvnc = { "main" : QHBoxLayout() }
        self.widgetAdvnc = { "arg"  : QSpinBox()    ,
                             "desc" : QLabel()      ,
                             "main" : QGroupBox()   }

        self.widgetAdvnc["arg"].setMinimum  ( 0 )
        self.widgetAdvnc["arg"].setMaximum  ( self.data["width"] - 1 )
        self.widgetAdvnc["arg"].setAlignment( Qt.AlignRight )
        self.widgetAdvnc["arg"].setMaximumWidth( 80 )

        self.widgetAdvnc["desc"].setText( self.getDesc() )

        self.widgetAdvnc["main"].setLayout( self.layoutAdvnc["main"] )
        self.layoutAdvnc["main"].setDirection( QBoxLayout.RightToLeft  )

        self.layoutAdvnc["main"].addWidget( self.widgetAdvnc["arg"]  )
        self.layoutAdvnc["main"].addWidget( self.widgetAdvnc["desc"] )
        self.widgetAdvnc["main"].setTitle ( "Advanced Options" )
        # SIZE MAIN -> (75,76)

        for w in self.widgetAdvnc.values():
            w.hide()

    def build_closeWButtons( self ):
        self.layoutClose = QHBoxLayout()
        self.widgetClose = { "buttons" : QDialogButtonBox( QDialogButtonBox.Ok 
                                                         | QDialogButtonBox.Cancel ) }

        # SIZE BUTTONS -> (166,26)
        self.layoutClose.addStretch(1)
        self.layoutClose.addWidget( self.widgetClose["buttons"] )

    def build_body( self ):
        self.layoutBody = QVBoxLayout()

        self.layoutBody.addLayout( self.layoutSettings["main"] )
        self.layoutBody.addWidget( self.widgetColor["main"]    )
        self.layoutBody.addWidget( self.widgetAdvnc["main"]    )
        self.layoutBody.addLayout( self.layoutClose            )

        # Final Building up:
        # NOTE: This layout have a default spacing of 6px
        self.window.setLayout( self.layoutBody )

    # TODO: Add more configuration
    def __adjust_components__( self ):
        self.window.setFixedWidth ( self.width  )
        self.window.setFixedHeight( self.height )

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
        self.advanced_connect()
        self.closing_connect()


    def __update__method_depends__( self ):
        index = self.widgetSettings["method"].currentIndex()
        self.data["method"] = index
        self.methodPreview.setIconFromIndex( index )
        self.__update_adv_visibility__()

    def __update_adv_visibility__( self ):
        index = self.data["method"]
        extra = self.data["has-extra"]
        if   index < 2:
            if extra:
                for widget in self.widgetAdvnc.values():
                    widget.hide()
                self.resize( self.width , self.height - self.extraHeight )
            # TODO: Fix resize problem. Only adjust the window size (for corners/classic) when you
            #       pass from (corners/classic) to (corners/classic) after select (*combined or *sequential)
            self.data["has-extra"] = False
        else:
            if not extra:
                for widget in self.widgetAdvnc.values():
                    widget.show()
                self.resize( self.width , self.height + self.extraHeight )
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


    def __update__advArg_depends__( self ):
        self.data["extra-arg"] = self.widgetAdvnc["arg"].value()

    def advanced_connect( self ):
        self.widgetAdvnc["arg"].valueChanged.connect( self.__update__advArg_depends__ )

    def report_data( self ):
        print( "Sending Data: {" )
        for k , v in self.data.items():
            print( f"{' ':4}{k} , {v}" )
        print( "}" )

    def closing_connect( self ):
        self.widgetClose["buttons"].accepted.connect( self.call_borderizer )
        self.widgetClose["buttons"].rejected.connect( self.window.close    )

    def call_borderizer( self ):
        self.report_data()

    def setup_size_constraints( self ):
        self.widgetSettings["LBody"].setFixedHeight( self.height * PROPORTION["settings"][1] )
        self.widgetSettings["RBody"].setFixedHeight( self.height * PROPORTION["settings"][1] )

        self.widgetColor["main"].setFixedHeight   ( self.height * PROPORTION["colors"][1]   )
        self.widgetAdvnc["main"].setFixedHeight   ( self.height * PROPORTION["advanced"][1] )
        self.widgetClose["buttons"].setFixedHeight( self.height * PROPORTION["close"][1]    )

        self.window.setFixedWidth( self.width )

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
