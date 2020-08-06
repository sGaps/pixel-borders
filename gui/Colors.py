# Module:      gui.Colors.py | [ Language Python ]
# Created by: ( Gaps | sGaps | ArtGaps )
# ------------------------------------------------
from PyQt5.QtWidgets import ( QPushButton , QGroupBox ,     # Widgets
                              QHBoxLayout , QLayout )       # Layouts
from PyQt5.QtCore    import pyqtSlot , pyqtSignal

# TODO: Add a third button: "Custom" and a third option ==> press_cs( self ) -> "CS"
class ColorButtons( QGroupBox ):
    """ Holds some buttons to select a color
        SIGNALS:
            void fg_released
            void bg_released
        SLOTS:
            void press_fg   => emits fg_released
            void press_bg   => emits bg_released
    """
    fg_released    = pyqtSignal()
    bg_released    = pyqtSignal()
    def __init__( self , parent = None ):
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

        self.setLayout( self.Lmain )
        self.setTitle( "Color Settings" )

        self.FGbut.released.connect( self.press_fg )
        self.BGbut.released.connect( self.press_bg )

    @pyqtSlot()
    def press_fg( self ):
        """ Ensures exclusive buttons. Returns 'FG' as result """
        self.FGbut.setChecked( True  )
        self.BGbut.setChecked( False )
        self.fg_released.emit()

    @pyqtSlot()
    def press_bg( self ):
        """ Ensures exclusive buttons. Returns 'BG' as result """
        self.BGbut.setChecked( True  )
        self.FGbut.setChecked( False )
        self.bg_released.emit()

