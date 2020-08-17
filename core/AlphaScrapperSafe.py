# Module:      core.AlphaScrapperSafe.py | [ Language Python ]
# Created by: ( Gaps | sGaps | ArtGaps )
# ------------------------------------------------------------
""" Defines an Scrapper object to extract the alpha data of a krita node.
    It accepts a transparent value and a threshold.
    This transparent & threshold value types corresponds to node.colorDepth()
    It means, they can be floats or ints. """
# @DEPRECATED:
from .PxDataStream import PxDataStream , LittleEndian , ReadMode , Float32 , UInt , Float
from PyQt5.QtCore  import QRect
from struct        import pack , unpack
# @DEPRECATED:
from array         import array

DEPTHS = { "U8"  : "B" ,
           "U16" : "H" ,
           "F16" : "e" ,
           "F32" : "f" }
        
class Scrapper( object ):
    TRANSPARENT = 0x00
    OPAQUE      = 0xff
    """ Utility class for extract the alpha channel from a krita node. """
    def __init__( self ):
        pass

    # TODO: Optimize. How?, pass the node bounds [NRect] + grow bounds [GRect] to
    #       extract exactly you need for this.
    # TODO: return the size of the byte size of the structure.
    def extractRelevantAlpha( self , node , extra_pixels = 0 , transparent = 0 , threshold = 0 ):
        """ returns the a simplified version of the alpha channel of the node (only marks if the pixel
            is or not transparent) with a lightly modification on its dimensions given by
            extra_pixels, and also returns the node bounds. """
        if node is None:
            return ( bytearray() , QRect() )
        bounds  = node.bounds()
        if bounds.width() == 0 or bounds.height() == 0:
            return ( bytearray() , QRect() )

        nbounds = QRect( bounds.x()      -   extra_pixels ,
                         bounds.y()      -   extra_pixels ,
                         bounds.width()  + 2*extra_pixels ,
                         bounds.height() + 2*extra_pixels )
        print( f"rect = ({nbounds.x()},{nbounds.y()},{nbounds.width()},{nbounds.height()})" )
        return (Scrapper.__extract_alpha__( node            , 
                                            nbounds.x()     ,
                                            nbounds.y()     ,
                                            nbounds.width() ,
                                            nbounds.height(),
                                            transparent     , 
                                            threshold       ) , nbounds )

    # TODO: return the size of the byte size of the structure.
    def extractAlpha( self , node , bounds , transparent = 0 , threshold = 0 ):
        if node is None or bounds.width() == 0 or bounds.height() == 0:
            return bytearray()
        return Scrapper.__extract_alpha__( node            ,
                                           bounds.x()      ,
                                           bounds.y()      ,
                                           bounds.width()  ,
                                           bounds.height() ,
                                           transparent     ,
                                           threshold       )

    @classmethod
    def __extract_alpha__( cls , node , x , y , w , h , transparent = 0 , threshold = 0 ):
        """ Extract the alpha pixel data from the node, using the coordinates x and y, and
            the sizes w and h (width and height).
            transparent , threshold :: Number """
        # Extract the channel information:
        wopaque      = Scrapper.OPAQUE
        wtransparent = Scrapper.TRANSPARENT

        chans = node.channels()
        if chans:
            nmChn  = len( chans )
            szChn  = chans[0].channelSize()
        else:
            nmChn = 1                       # 1 channel
            szChn = 1                       # 1 byte

        pxldata = bytes( node.projectionPixelData( x , y , w , h ) )
        pattern = DEPTHS[node.colorDepth()]

        low    = transparent - threshold
        high   = transparent + threshold

        if pattern == DEPTHS["F16"]:
            # Special treats
            offset = (nmChn - 1) * szChn
            step   = nmChn * szChn
            length = len(pxldata)
            tsize  = 2
            reader = memoryview( pxldata ).cast( 'B' )
            # NOTE: read the values as Float 16 using the struct.unpack interface, because I'm having
            #       some troubles trying read them using the memoryview.cast( 'e' )
            return bytearray( wtransparent if low <= unpack( pattern , reader[i:i+tsize] )[0] <= high else
                              wopaque      for i in range(offset,length,step) )
        else:
            offset = nmChn - 1
            step   = nmChn
            reader = memoryview( pxldata ).cast( pattern )
            length = len( reader )
            # TODO: I think this must be wtransparent if low <= ...
            return bytearray( wtransparent if low <= reader[i] <= high else
                              wopaque      for i in range(offset,length,step) )

    def channelSize( self , node ):
        """ Returns the channel size of the channels inside the node. """
        chans = node.channels()
        return chans[0].channelSize() if chans else 1

    def channelNumber( self , node ):
        """ Returns the number of channels inside the node. """
        chans = node.channels()
        return len(chans) if chans else 1

