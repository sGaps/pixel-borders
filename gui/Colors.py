# Module:      gui.Colors.py | [ Language Python ]
# Created by: ( Gaps | sGaps | ArtGaps )
# ------------------------------------------------
from PyQt5.QtWidgets import (   # Widgets ---------------
                                QPushButton , QGroupBox , 
                                # Layouts ---
                                QHBoxLayout , QLayout )

# TODO: Add a third button: "Custom" and a third option ==> press_cs( self ) -> "CS"
class ColorButtons( QGroupBox ):
    """ Contains and show a image """
    def __init__( self , width , height , parent = None ):
        super().__init__( parent )
        self.Lmain = QHBoxLayout()
        self.FGbut = QPushButton( "Foreground" )
        self.BGbut = QPushButton( "Background" )

        self.Lmain.addWidget( self.FGbut )
        self.Lmain.addWidget( self.BGbut )
        self.Lmain.setSizeConstraint( QLayout.SetDefaultConstraint )

        self.FGbut.setCheckable( True )
        self.BGbut.setCheckable( True )
        self.FGbut.setChecked( True  )
        self.BGbut.setChecked( False )

        self.setLayout( Lmain )
        self.setTitle( "Color Settings" )

        self.__setup_size__( width , height )
        self.__setup_exclusive_buttons__()

    def __setup_size__( self , width , height ):
        pass

    def press_fg( self ):
        """ Ensures exclusive buttons. Returns 'FG' as result """
        self.FGbut.setChecked( True  )
        self.BGbut.setChecked( False )
        return "FG"

    def press_bg( self ):
        """ Ensures exclusive buttons. Returns 'BG' as result """
        self.BGbut.setChecked( True  )
        self.FGbut.setChecked( False )
        return "BG"

    def __action_press_fg__( self ):
        self.data["color"] = press_fg()
    
    def __action_press_bg__( self , data ):
        self.data["color"] = press_bg()

    def auto_connect_with_data( self , data ):
        self.data = data
        self.connect_to_updates( self.__action_press_fg__ , self.__action_press_bg__ )

    def connect_to_updates( self , on_fg_press , on_bg_press ):
        """ Connect the actions that will to perform after press the buttons. """
        self.FGbut.released.connect( on_fg_press )
        self.BGbut.released.connect( on_bg_press )

