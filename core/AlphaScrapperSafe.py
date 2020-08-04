# Module:      core.AlphaScrapperSafe.py | [ Language Python ]
# Created by: ( Gaps | sGaps | ArtGaps )
# ------------------------------------------------------------
""" Defines an Scrapper object to extract the alpha data of a krita node.
    It accepts a transparent value and a threshold.
    This transparent & threshold value types corresponds to node.colorDepth()
    It means, they can be floats or ints. """
from .PxDataStream import PxDataStream , LittleEndian , ReadMode , Float32

TRANSPARENT = 0x00
OPAQUE      = 0xff
class Scrapper( object ):
    """ Utility class for extract the alpha channel from a krita node. """
    def __init__( self ):
        pass

    def extractAlpha( self , node , bounds , transparent = 0 , threshold = 0 ):
        """ Extract the alpha pixel data from the node, using bounds which is a QRect-like object.
            transparent :: Number """
        if node is None or bounds.width() == 0 or bounds.height() == 0:
            return bytearray()
        pxldata = node.projectionPixelData( bounds.x()      , 
                                            bounds.y()      , 
                                            bounds.width()  , 
                                            bounds.height() )
        # Extract the channel information:
        chans = node.channels()
        if chans:
            nmChn = len( chans )
            szChn = chans[0].channelSize()
        else:
            nmChn = 1                       # 1 channel
            szChn = 1                       # 1 byte

        index  = 0
        result = bytearray( pxldata.size() // (szChn*nmChn) )
        stream = PxDataStream( pxldata , node.colorDepth() , ReadMode , LittleEndian , Float32 )
        while not stream.atEnd():
            for i in range( nmChn - 1 ):
                stream.ignoreValue()

            # This permits floating point safe comparison:
            if transparent - threshold <= stream.readValue() <= transparent + threshold:
                result[index] = TRANSPARENT
            else:
                result[index] = OPAQUE
            index += 1
        return result

    def channelSize( self , node ):
        """ Returns the channel size of the channels inside the node. """
        chans = node.channels()
        return chans[0].channelSize() if chans else 1

    def channelNumber( self , node ):
        """ Returns the number of channels inside the node. """
        chans = node.channels()
        return len(chans) if chans else 1

