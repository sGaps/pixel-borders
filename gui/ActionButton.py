from PyQt5.QtWidgets    import ( QWidget , QStackedWidget , QVBoxLayout , QHBoxLayout , QLayout , # Used in Menu
                                 QPushButton , QSizePolicy )              # Used in ActionButtons
ICONS = {   "OK" : () ,
            "X"  : () ,
            ">"  : () ,
            "<"  : () ,
            "?"  : () ,
            "_"  : () }
TYPES = { "Accept" : "OK" ,
          "Cancel" : "X"  ,
          "Info"   : "?"  }

class ActionButton( QPushButton ):
    ACCEPT = "OK"
    CANCEL = "X"
    NEXT   = ">"
    PREV   = "<"
    INFO   = "?"
    NONE   = "_"
    def __init__( self , parent = None ):
        super().__init__( parent )
        self.type = ActionButton.NONE
        #self.setSizePolicy( QSizePolicy.Preferred , QSizePolicy.Preferred )
        self.setGeometry( 0 , 0 , 100 , 100 )

    def load_icon( self , icon_name ):
        pass
