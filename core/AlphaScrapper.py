# Module:      AlphaScrapper.py | [ Language Python ]
# Created by: ( Gaps | sGaps | ArtGaps )
# ---------------------------------------------------

TRANSPARENT = b"\x00"
OPAQUE      = b"\xff"

class Scrapper( object ):
    """ Utility class for extract the alpha channel from a krita node. """
    def __init__( self ):
        pass

    # Uses the function for fast indexing PyQt5.QtCore.QByteArray::at( int index ) -> char
    def isOpaqueAt( self , i , raw , sz ):
        for byte in range(sz):
            if raw.at(i + byte) == TRANSPARENT: return False
        return True

    # TODO: Change doc for bounds object
    def extractAlpha( self , node , doc , opaque = 0xFF , transparent = 0x00 ):
        if node is None or doc is None:
            return bytearray()

        nmChn   = len( node.channels() )            # Number of Channels.
        szChn   = node.channels()[0].channelSize()  # Channel size.

        # Document bounds & Pixel data:
        bounds  = doc.bounds()
        rawdata = node.projectionPixelData( bounds.x()      , 
                                            bounds.y()      , 
                                            bounds.width()  , 
                                            bounds.height() )
        size    = rawdata.size()                    # size of pdata.
        step    = nmChn * szChn                     # steps of search.

        if bounds.width() == 0 or bounds.height() == 0:
            return bytearray()
        
        offset  = (nmChn - 1) * szChn
        return bytearray( opaque      if  self.isOpaqueAt(index,rawdata,szChn) else
                          transparent for index in range(offset,size,step) )

# -------------------------------------------------------------
# TODO: REMOVE THIS
if __name__ == "__main__":
    from krita import Krita
    kis = Krita.instance()
    d = kis.activeDocument()
    n = d.activeNode()
    s = Scrapper()
    data = s.extractAlpha(n,d)
    print( data )
# -------------------------------------------------------------
