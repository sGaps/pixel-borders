from PyQt5.QtWidgets import QWidget , QFormLayout , QPushButton , QLineEdit
from .Page import Page

class NameContents( QWidget ):
    def __init__( self , parent = None ):
        super().__init__( parent )
        # Layout setup:
        self.layout = QFormLayout()
        self.setLayout( self.layout )

        # Widgets setup:
        self.line   = QLineEdit()
        self.layout.addRow( "Name" , self.line )

    def name():
        return self.line.text()


class NamePage( Page ):
    def __init__( self , prevP = None , nextP = None , parent = None ):
        super().__init__( prevP , nextP , parent )
        self.includeWidget( NameContents() , "name" )

    def getData( self ):
        w = self.getWidget( "name" )
        return { "name" : w.name() if w else "" }

