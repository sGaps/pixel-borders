# Module:   gui.About.py | [ Language Python ]
# Author:   Gaps | sGaps | ArtGaps
# LICENSE:  GPLv3 (available in ./LICENSE.txt)
# --------------------------------------------
"""
    Module used to display information about this plugin.

    [:] Defined in this module
    --------------------------
    ButtonWithUrl :: class
        Opens the browser with an specific url.

    About :: class
        Shows information about this plugin
"""
from PyQt5.QtCore     import Qt , pyqtSignal , pyqtSlot , QUrl
from PyQt5.QtWidgets  import ( QDialog , QPushButton , QLabel , QWidget ,
                               QVBoxLayout , QFormLayout )
from PyQt5.QtGui      import QDesktopServices
from .MenuPage        import subTitleLabel


class ButtonWithUrl( QPushButton ):
    """ Creates a button with a URL. Opens the url in the default browser if it's pressed. """
    def __init__( self , text = "button" , url = None , flat = True , parent = None ):
        super().__init__( text , parent )
        self.setFlat( flat )
        self.url = QUrl( url , QUrl.TolerantMode )
        if url:
            self.setToolTip( url )
            self.clicked.connect( self.openUrl )

    @pyqtSlot()
    def openUrl( self ):
        QDesktopServices.openUrl( self.url )

class About( QDialog ):
    """ Shows information about this plugin """

    def __init__( self , parent = None ):
        super().__init__( parent )

        self.layout = QVBoxLayout( self )
        self.wabout = QWidget()
        self.fabout = QFormLayout( self.wabout )

        self.name   = subTitleLabel( "Pixel Borders" )
        self.desc   = QLabel( "Make borders for your pixelart characters" )
        self.s1     = QLabel()
        self.s2     = QLabel()

        self.autorS = subTitleLabel( "Author:" )
        self.autorN = ButtonWithUrl( "ArtGaps / sGaps / Gaps" )
        self.source = subTitleLabel( "Repository:" )

        self.follwS = subTitleLabel( "Follow Me On:" )
        self.PixivU = ButtonWithUrl( "Pixiv"       , "https://pixiv.me/artgaps"                 )
        self.NewGrU = ButtonWithUrl( "Newgrounds"  , "https://artgaps.newgrounds.com"           )
        self.GitHbU = ButtonWithUrl( "Github"      , "https://github.com/sGaps"                 )
        self.DeviAU = ButtonWithUrl( "DeviantArt"  , "https://www.deviantart.com/artgaps"       )
        self.TwttrU = ButtonWithUrl( "Twitter"     , "https://twitter.com/ArtGaps"              )
        self.SrcCoD = ButtonWithUrl( "Source Code" , "https://github.com/sGaps/pixel-borders"   )


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

        self.fabout.setWidget( 6 , QFormLayout.LabelRole , self.s2     )
        self.fabout.setWidget( 7 , QFormLayout.FieldRole , self.SrcCoD )
        self.fabout.setWidget( 7 , QFormLayout.LabelRole , self.source )


        # Layout setup
        self.layout.addWidget( self.name , 0 , Qt.AlignCenter )
        self.layout.addWidget( self.desc , 1 , Qt.AlignCenter )
        self.layout.addWidget( self.s1 )
        self.layout.addWidget( self.wabout )
        self.layout.addWidget( self.okay , 3 , Qt.AlignBottom | Qt.AlignRight )

        # connections
        self.okay.clicked.connect( self.accept )
        # tab order:
        # 1. About, 2. Social media, 3. Repository
        QWidget.setTabOrder( self.okay   , self.autorN )
        QWidget.setTabOrder( self.autorN , self.PixivU )
        QWidget.setTabOrder( self.PixivU , self.NewGrU )
        QWidget.setTabOrder( self.NewGrU , self.DeviAU )
        QWidget.setTabOrder( self.DeviAU , self.GitHbU )
        QWidget.setTabOrder( self.GitHbU , self.TwttrU )
        QWidget.setTabOrder( self.TwttrU , self.SrcCoD )

