# Module:      gui.Colors.py | [ Language Python ]
# Created by: ( Gaps | sGaps | ArtGaps )
# ------------------------------------------------
from PyQt5.QtWidgets import ( QPushButton , QGroupBox , QLabel ,                        # Widgets
                              QVBoxLayout , QHBoxLayout , QLayout , QFormLayout )       # Layouts
from PyQt5.QtCore     import pyqtSlot , pyqtSignal

# TODO: Add a third button: "Custom" and a third option ==> press_cs( self ) -> "CS"
class ColorButtons( QGroupBox ):
    """ Holds some buttons to select a color
        SIGNALS:
            void fg_released
            void bg_released
            void cs_released
        SLOTS:
            void press_fg   => emits fg_released
            void press_bg   => emits bg_released
            void press_cs   => emits cs_released
    """
    fg_released    = pyqtSignal()
    bg_released    = pyqtSignal()
    cs_released    = pyqtSignal()
    def __init__( self , parent = None ):
        super().__init__( parent )
        self.Lmain = QVBoxLayout()
        self.Lbutn = QHBoxLayout()
        self.FGbut = QPushButton( "Foreground" )
        self.BGbut = QPushButton( "Background" )
        # TODO: Add a krita connection here
        self.CSbut = QPushButton( "Custom" )
        self.LSub  = QFormLayout()
        self.WComp = None
        self.Wname = None
        self.KConn = False

        self.Lmain.addLayout( self.Lbutn )

        self.Lbutn.addWidget( self.FGbut )
        self.Lbutn.addWidget( self.BGbut )
        self.Lbutn.addWidget( self.CSbut )
        self.Lbutn.setSizeConstraint( QLayout.SetDefaultConstraint )

        self.FGbut.setCheckable( True )
        self.BGbut.setCheckable( True )
        self.FGbut.setChecked( True  )
        self.BGbut.setChecked( False )

        self.setLayout( self.Lmain )
        self.setTitle( "Color Settings" )
        self.CSbut.hide()

        self.FGbut.released.connect( self.press_fg )
        self.BGbut.released.connect( self.press_bg )
        self.CSbut.released.connect( self.press_cs )

    # TODO: Fix Render.
    def tryCustomBuild( self , node , SpinBoxFactory ):
        self.CSbut.show()
        # Only Read-Mode
        depth      = node.colorDepth()
        self.WComp = []
        self.Wname = []
        for c in node.channels():
            spin = SpinBoxFactory(depth)
            name = QLabel( c.name() )
            self.LSub.addRow( name , spin )
            self.WComp.append( spin )
            self.Wname.append( name )
        self.Lmain.addLayout( self.LSub )
        self.hide_components()
        self.KConn = True

    def getComponents( self ):
        if self.WComp:
            return [ c.value() for c in self.WComp ]
        else:
            return None

    @pyqtSlot()
    def hide_components( self ):
        for i in range( len(self.WComp) ):
            self.WComp[i].hide()
            self.Wname[i].hide()

    @pyqtSlot()
    def show_components( self ):
        for i in range( len(self.WComp) ):
            self.WComp[i].show()
            self.Wname[i].show()

    @pyqtSlot()
    def press_cs( self ):
        self.FGbut.setChecked( False )
        self.BGbut.setChecked( False )
        if self.KConn:
            self.CSbut.setChecked( True  )
            self.show_components()
        self.cs_released.emit()


    @pyqtSlot()
    def press_fg( self ):
        """ Ensures exclusive buttons. Returns 'FG' as result """
        self.FGbut.setChecked( True  )
        self.BGbut.setChecked( False )
        if self.KConn:
            self.CSbut.setChecked( False )
            self.hide_components()
        self.fg_released.emit()

    @pyqtSlot()
    def press_bg( self ):
        """ Ensures exclusive buttons. Returns 'BG' as result """
        self.BGbut.setChecked( True  )
        self.FGbut.setChecked( False )
        if self.KConn:
            self.CSbut.setChecked( False )
            self.hide_components()
        self.bg_released.emit()

