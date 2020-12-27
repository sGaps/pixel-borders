from PyQt5.QtCore     import Qt , pyqtSignal , pyqtSlot , QUrl
from PyQt5.QtWidgets  import ( QDialog , QPushButton , QLabel , QWidget ,
                               QVBoxLayout , QFormLayout )
from PyQt5.QtGui      import QDesktopServices
from MenuPage         import subTitleLabel


class ButtonWithUrl( QPushButton ):
    def __init__( self , text = "button" , url = None , flat = True , parent = None ):
        super().__init__( text , parent )
        self.setFlat( flat )
        self.url = QUrl( url , QUrl.TolerantMode )
        if url:
            self.setToolTip( url )
            self.released.connect( self.openUrl )


    @pyqtSlot()
    def openUrl( self ):
        QDesktopServices.openUrl( self.url )

class About( QDialog ):
    def __init__( self , parent = None ):
        super().__init__( parent )

        self.layout = QVBoxLayout( self )
        self.wabout = QWidget()
        self.fabout = QFormLayout( self.wabout )

        self.autorS = subTitleLabel( "Author:" )
        self.autorN = ButtonWithUrl( "ArtGaps / sGaps / Gaps" )

        self.follwS = subTitleLabel( "Follow Me On:" )
        self.PixivU = ButtonWithUrl( "Pixiv"      , "https://pixiv.me/artgaps"       )
        self.NewGrU = ButtonWithUrl( "Newgrounds" , "https://artgaps.newgrounds.com" )
        self.GitHbU = ButtonWithUrl( "Github"     , "https://github.com/sGaps" )
        self.DeviAU = ButtonWithUrl( "DeviantArt" , "https://www.deviantart.com/artgaps" )
        self.TwttrU = ButtonWithUrl( "Twitter"    , "https://twitter.com/ArtGaps" )


        self.okay   = QPushButton( "Got it! " )

        # Form setup
        self.fabout.setWidget( 0 , QFormLayout.LabelRole , self.autorS )
        self.fabout.setWidget( 0 , QFormLayout.FieldRole , self.autorN )

        self.fabout.setWidget( 1 , QFormLayout.LabelRole , self.follwS )
        self.fabout.setWidget( 1 , QFormLayout.FieldRole , self.PixivU )
        self.fabout.setWidget( 2 , QFormLayout.FieldRole , self.NewGrU )
        self.fabout.setWidget( 3 , QFormLayout.FieldRole , self.DeviAU )
        self.fabout.setWidget( 4 , QFormLayout.FieldRole , self.GitHbU )
        self.fabout.setWidget( 5 , QFormLayout.FieldRole , self.TwttrU )


        # Layout setup
        self.layout.addWidget( self.wabout )
        self.layout.addWidget( self.okay , 1 , Qt.AlignBottom | Qt.AlignRight )

        # connections
        self.okay.released.connect( self.accept )
        self.setTabOrder( self.okay , self.wabout )
