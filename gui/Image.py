# Module:      gui.Image.py | [ Language Python ]
# Created by: ( Gaps | sGaps | ArtGaps )
# -----------------------------------------------
from PyQt5.QtWidgets import QLabel
from PyQt5.QtGui     import QPixmap
from os              import path

this_module_dir = path.dirname( path.abspath(__file__) )
IMGDIRNAME      = "images/"
img_dir         = path.join( this_module_dir , IMGDIRNAME )

def pixmapFrom( relative_path ):
    return QPixmap( path.join(img_dir , relative_path) )
# Too big: 256x256 px
ICONS = { 0 : pixmapFrom( "classic.png" )            ,
          1 : pixmapFrom( "corners.png" )            ,
          2 : pixmapFrom( "classicThenCorners.png" ) ,
          3 : pixmapFrom( "cornersThenClassic.png" ) ,
          4 : pixmapFrom( "classicAndCorners.png"  ) ,
          5 : pixmapFrom( "classicAndCorners.png"  ) }

TABLE = { "classic"         : 0 ,
          "corners"         : 1 ,
          "classicTcorners" : 2 ,
          "cornersTclassic" : 3 ,
          "classic&corners" : 4 ,
          "corners&classic" : 5 }
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
        if index in ICONS:
            self.setPixmap( ICONS[index] )

    def setIcon( self , name ):
        if name in TABLE:
            self.setIconUsingIndex( TABLE[name] )


