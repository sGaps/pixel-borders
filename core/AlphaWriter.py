# Module:      core.AlphaWriter.py | [ Language Python ]
# Created by: ( Gaps | sGaps | ArtGaps )
# ------------------------------------------------------
""" Defines an Scrapper object to extract the alpha data of a krita node.
    It accepts a transparent value and a threshold.
    This transparent & threshold value types corresponds to node.colorDepth()
    It means, they can be floats or ints. """
from .PxDataStream import PxDataStream , LittleEndian , WriteMode , Float32 , UInt , Float
from PyQt5.QtCore  import QByteArray

TRANSPARENT = 0x00
OPAQUE      = 0xff
# TODO: Optimize!
class Writer( object ):
    def __init__pass( self ):
        pass
    # TODO: Write directly into the channel instead writting into the node pixel data
    def writeAlpha( self , node , bytedata , size , bounds , transparent = 0 ):
        """ opaque :: Number """

        depth = node.colorDepth()
        if depth[0] == UInt:
            opaque = 2**int(depth[1:]) - 1
        else:
            opaque = 1.0
        # Extract the channel information:
        chans = node.channels()
        if chans:
            nmChn = len( chans )
        else:
            nmChn = 1                       # 1 channel

        data   = QByteArray( size , b"\x00" )
        stream = PxDataStream( data , depth , WriteMode , LittleEndian , Float32 )
        stream.startTransaction()
        for b in bytedata:
            for c in range(nmChn-1):
                stream.ignoreValue()
            if b == TRANSPARENT:
                stream.writeValue( transparent )
            else:
                stream.writeValue( opaque      )
        if stream.commitTransaction():
            node.setPixelData( data            ,
                               bounds.x()      , 
                               bounds.y()      , 
                               bounds.width()  , 
                               bounds.height() )
