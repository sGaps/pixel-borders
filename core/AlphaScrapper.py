# Module:      GUI.py | [ Language Python ]
# Created by: ( Gaps | sGaps | ArtGaps )
# Using:      ( BBD's Krita Script Starter Feb 2018 )
# ---------------------------------------------------

TRANSPARENT = b"\x00"
OPAQUE      = b"\xff"

# TODO: Use node bounds instead document bounds for iterate over the bytearray.
# NOTE: Why?, well, It's because It will avoid iterate over the whole image in the average case.
class Scrapper( object ):
    def __init__( self ):
        pass

    def setData( self , node , doc ):
        self.node    = node                             # Node.
        self.nmChn   = len( node.channels() )           # Number of Channels.
        self.szChn   = node.channels()[0].channelSize() # Channel size.

        # Update pixelData:
        self.pxget   = self.node.projectionPixelData    # Pixel Data getter function.
        self.bounds  = doc.bounds()
        # TODO: Optimization here. Return directly this instead copy 2 times the same data.
        self.rawdata = self.pxget( self.bounds.x()      ,
                                   self.bounds.y()      , 
                                   self.bounds.width()  , 
                                   self.bounds.height() )
        self.size    = len( self.pxdata )               # size of pdata.
        self.step    = self.nmChn * self.szChn          # steps of search.

    def isOpaqueAt( self , i ):
        for byte in range(self.szChn):
            if self.rawdata.at(i + byte) == TRANSPARENT: return False
        return True

    # NOTE: This version is better than other two
    def extractAlpha( self , node , doc , opaque = 0xFF , transparent = 0x00 ):
        if node is None or doc is None:
            return bytearray()

        self.setData( node , doc )

        if not node or self.bounds.width() == 0 or self.bounds.height() == 0:
            return bytearray()
        
        offset  = (self.nmChn - 1) * self.szChn
        return bytearray( opaque      if  self.isOpaqueAt(index) else
                          transparent for index in range(offset,self.size,self.step) )

# -------------------------------------------------------------
# TODO: REMOVE THIS [INIT] ---\
if __name__ == "__main__":
    from krita import Krita
    kis = Krita.instance()
    d = kis.activeDocument()
    n = d.activeNode()
    s = Scrapper()
    data = s.extractAlpha(n,d)
    print( data )
# TODO: REMOVE THIS [END] ---/
# -------------------------------------------------------------
