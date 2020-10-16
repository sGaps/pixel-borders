# Module:      core.AlphaScrapper.py | [ Language Python ]
# Created by: ( Gaps | sGaps | ArtGaps )
# --------------------------------------------------------
"""
    [:] Defined in this module
    --------------------------

    Old and usafe version of the module gui.AlphaScrapperSafe.

    [*] Created By 
     |- Gaps : sGaps : ArtGaps
"""

class Scrapper( object ):
    """ Utility class for extract the alpha channel from a krita node. """
    def __init__( self ):
        pass

    def isOpaqueAt( self , i , rawdata , sz , transparent = 0x00  ):
        """ Returns true if there isn't transparent bytes in rawdata. """
        return rawdata.count( transparent , i , i+sz ) != sz

    def isTransparentAt( self , i , rawdata , sz , transparent = 0x00 ):
        """ Returns true if there is transparent bytes in rawdata. """
        return rawdata.find( transparent , i, sz ) > -1

    def extractAlpha( self , node , bounds , opaque = 0xFF , transparent = 0x00 ):
        """ Extract the alpha pixel data from the node, using bounds which is a QRect-like object. """
        if node is None or bounds.width() == 0 or bounds.height() == 0:
            return bytearray()
        
        # Extract the channel information:
        chans = node.channels()
        if chans:
            nmChn = len( chans )
            szChn = chans[0].channelSize()
        else:
            nmChn = 1                       # 1 channel
            szChn = 1                       # 1 byte

        # It uses the Pixel Projection Data for extract the information of the node even if its a group layer:
        rawdata = node.projectionPixelData( bounds.x()      , 
                                            bounds.y()      , 
                                            bounds.width()  , 
                                            bounds.height() )
        size    = rawdata.size()                    # size of pdata.
        step    = nmChn * szChn                     # steps of search.

        
        # Run into alpha channel:
        offset  = (nmChn - 1) * szChn
        return bytearray( opaque      if  self.isOpaqueAt(index,rawdata,szChn,transparent) else
                          transparent for index in range(offset,size,step) )

    def channelSize( self , node ):
        """ Returns the channel size of the channels inside the node. """
        chans = node.channels()
        return chans[0].channelSize() if chans else 1

    def channelNumber( self , node ):
        """ Returns the number of channels inside the node. """
        chans = node.channels()
        return len(chans) if chans else 1
