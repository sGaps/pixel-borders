# Module:   core.AlphaScrapperSafe.py | [ Language Python ]
# Author:   Gaps | sGaps | ArtGaps
# LICENSE:  GPLv3 (available in ./LICENSE.txt)
# ---------------------------------------------------------
"""
    Defines an Scrapper class to extract the alpha
    data of a Krita's Node. It accepts a transparent
    value with a threshold value

    The transparent and threshold values are the same
    **arguments** used in the node.colorDepth() function.

    [:] Defined in this module
    --------------------------
    Scrapper    :: class
        class used to extract the alpha channel from a Krita's node.

    DEPTHS      :: dict
        Holds relevant information about color depths supported by Krita.

    [*] Author
     |- Gaps : sGaps : ArtGaps
"""


from PyQt5.QtCore  import QRect
from struct        import pack , unpack

DEPTHS = { "U8"  : "B" ,    # unsigned char
           "U16" : "H" ,    # unsigned short
           "F16" : "e" ,    # half float
           "F32" : "f" }    # float

class Scrapper( object ):
    """ Utility class to extract the alpha channel from a Krita's Node. """
    TRANSPARENT = 0x00
    OPAQUE      = 0xff
    def __init__( self ):
        """ Defined only for compatibility purposes. """
        pass

    def extractRelevantAlpha( self , node , extra_pixels = 0 , transparent = 0 , threshold = 0 ):
        """
            ARGUMENTS
                node (krita.Node):      The source node.
                extra_pixels(int):      number of pixels that will be added to the bound box size.
                transparent(number):    The value which is considered as transparent.
                threshold(number):      The range of values that the class will consider as transparent.
            RETURNS
                ( bytearray , QRect )

            returns a simplified version of the Node's alpha channel (only marks if the pixel
            is transparent or not) with a lightly modification on its dimensions given by
            the variable extra_pixels, and also returns the node bounds. """
        if node is None:
            return ( bytearray() , QRect() )
        bounds  = node.bounds()
        if bounds.width() == 0 or bounds.height() == 0:
            return ( bytearray() , QRect() )

        nbounds = QRect( bounds.x()      -   extra_pixels ,
                         bounds.y()      -   extra_pixels ,
                         bounds.width()  + 2*extra_pixels ,
                         bounds.height() + 2*extra_pixels )
        return (Scrapper.__extract_alpha__( node            ,
                                            nbounds.x()     ,
                                            nbounds.y()     ,
                                            nbounds.width() ,
                                            nbounds.height(),
                                            transparent     ,
                                            threshold       ) , nbounds )

    def extractAlpha( self , node , bounds , transparent = 0 , threshold = 0 ):
        """
            ARGUMENTS
                node (krita.Node):          The source node.
                bounds(PyQt5.QtCore.QRect): The bounds that will be used to extract the alpha values.
                transparent(number):        The value which is considered as transparent.
                threshold(number):          The range of values that the class will consider as transparent.
            RETURNS
                bytearray

            Extract a simplified version of the Node's alpha channel. This only
            marks the opaque pixels with the 0xff value and the transparent ones with 0x00.
            """
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
        """
            ARGUMENTS
                node (krita.Node):          The source node.
                x(int):                     Top-left-x coordinate.
                y(int):                     Top-left-y coordinate.
                w(int):                     width of the node's bound.
                h(int):                     height of the node's bound.
                transparent(number):        The value which is considered as transparent.
                threshold(number):          The range of values that the class will consider as transparent.
            RETURNS
                bytearray

            Extract the alpha pixel data from the node, using the coordinates x and y, and
            the sizes w and h (width and height).
            """
        # Extract the channel data:
        wopaque      = Scrapper.OPAQUE
        wtransparent = Scrapper.TRANSPARENT

        chans = node.channels()
        if chans:
            nmChn  = len( chans )
            szChn  = chans[0].channelSize()
        else:
            nmChn = 1                       # 1 channel
            szChn = 1                       # 1 byte

        # Retrive the projection Information: (THIS ALLOWS GROUP LAYERS SUPPORT)
        pxldata = bytes( node.projectionPixelData( x , y , w , h ) )
        pattern = DEPTHS[node.colorDepth()]
        low    = transparent - threshold
        high   = transparent + threshold

        if pattern == DEPTHS["F16"]:
            # Special traits:
            offset = (nmChn - 1) * szChn
            step   = nmChn * szChn
            length = len(pxldata)
            tsize  = 2
            reader = memoryview( pxldata ).cast( 'B' )
            # NOTE: this reads the values as Float16 using the built-in interface ```struct.unpack```,
            #       because this had some troubles when tries to read them using the memoryview.cast( 'e' )
            return bytearray( wtransparent if low <= unpack( pattern , reader[i:i+tsize] )[0] <= high else
                              wopaque      for i in range(offset,length,step) )
        else:
            offset = nmChn - 1
            step   = nmChn
            reader = memoryview( pxldata ).cast( pattern )
            length = len( reader )
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
