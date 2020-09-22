# Module:      gui.Preview.py | [ Language Python ]
# Created by: ( Gaps | sGaps | ArtGaps )
# -------------------------------------------------
from PyQt5.QtWidgets import QLabel
from PyQt5.QtGui     import QPixmap
from os              import path

this_module_dir = path.dirname( path.abspath(__file__) )
IMGDIRNAME      = "images/"
img_dir         = path.join( this_module_dir , IMGDIRNAME )

def pixmapFrom( relative_path ):
    return QPixmap( path.join(img_dir , relative_path) )
# Too big: 256x256 px

ICONS = [ pixmapFrom( "force.png" )        ,
          pixmapFrom( "any-neighbor.png" ) ,
          pixmapFrom( "corners.png"      ) ,
          pixmapFrom( "not-corners.png"  ) ,
          pixmapFrom( "custom.png"       ) ]
ICON_NUMBER  = len(ICONS)
CUSTOM_INDEX = ICON_NUMBER - 1

TABLE = { "force"           : 0 ,
          "any-neighbor"    : 1 ,
          "corners"         : 2 ,
          "not-corners"     : 3 ,
          "customs"         : 4 }

# Use __file__ for get the path
class Preview( QLabel ):
    def __init__( self , parent = None ):
        super().__init__( parent )

    def loadImg( self , relative_path ):
        self.setPixmap( self.__qpixmap_from_rpath__(relative_path) )

    def __qpixmap_from_rpath__( self , relative_path ):
        absolute_path = path.join( this_module_dir , relative_path )
        return QPixmap( absolute_path )

    def setIconFromIndex( self , index ):
        if 0 <= index <= ICON_NUMBER:
            self.setPixmap( ICONS[index] )

    def setIcon( self , name ):
        if name in TABLE:
            self.setIconUsingIndex( TABLE[name] )


