from PyQt5.QtCore       import QRect
from PyQt5.QtWidgets    import ( QDialog , QStackedWidget , QVBoxLayout , QHBoxLayout , QLayout , QLabel , # Used in Menu
                                 QPushButton )              # Used in ActionButtons
from .Page import *

class Menu( QDialog ):
    def __init__( self , title = "PxGUI" , size_constraint = QLayout.SetFixedSize , parent = None ):
        super().__init__( parent )
        self.setWindowTitle( title )
        
        # Layout setup:
        self.layout  = QVBoxLayout()
        self.setLayout( self.layout )
        self.layout.setSizeConstraint( size_constraint )

        # Main Widget:
        self.main = QStackedWidget()
        self.pages = {}

        # Setup buttons:
        self.layout.addWidget( self.main )

    def addPage( self , page , name ):
        if name not in self.pages:
            self.pages[name] = page
            self.main.addWidget( page )
            # setup connections:
            page.Lbut.released.connect( self.on_lpress )
            page.Rbut.released.connect( self.on_rpress )

    def loadPage( self , page ):
        index = self.main.indexOf( page )
        if index < 0:
            return False
        else:
            self.main.setCurrentWidget( page )

    def on_rpress( self ):
        page = self.main.currentWidget()
        if page:
            self.loadPage( page.getNext() )

    def on_lpress( self ):
        index = self.main.currentIndex()
        page  = self.main.widget( index )
        if page:
            self.loadPage( page.getPrev() )

    def on_cancel( self ):
        pass

    def on_accept( self ):
        pass


