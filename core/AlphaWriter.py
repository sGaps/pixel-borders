# Module:      core.AlphaWriter.py | [ Language Python ]    @DEPRECATED . CAN BE DELETED
# Created by: ( Gaps | sGaps | ArtGaps )
# ------------------------------------------------------
""" Defines an Scrapper object to extract the alpha data of a krita node.
    It accepts a transparent value and a threshold.
    This transparent & threshold value types corresponds to node.colorDepth()
    It means, they can be floats or ints. """
#@DEPRECATED
from .PxDataStream import PxDataStream , LittleEndian , WriteMode , Float32 , UInt , Float
from PyQt5.QtCore  import QByteArray
from struct        import pack , unpack

TRANSPARENT = 0x00
OPAQUE      = 0xff

# TODO: Optimize!
DEPTHS = { "U8"  : ('B',2**8 -1,1) ,
           "U16" : ('H',2**16-1,2) ,
           "F16" : ('e',1.0  ,2) ,
           "F32" : ('f',1.0  ,4) }
# TODO: Krita fails everytime I try to do something with her! >:(
#       There's lots of inconcistencies between the Krita behavior and
#       the API documentation. I wish it were more detailed...
class Writer( object ):
    def __init__pass( self ):
        pass


    def replace_alpha( self , alphadata , alength , rawdata , nchans , depth , rlength ):
        CONTEXT = DEPTHS[depth]
        TYPE    = CONTEXT[0]
        OPAQUE  = CONTEXT[1]
        nbytes  = CONTEXT[2]
        AOPAQUE = 255
        TRANSPARENT = 0

        assert nbytes * nchans * alength == rlength

        reader = memoryview( alphadata ).cast( 'B' )
        if TYPE == 'e': # Float 16
            szChn  = 2
            offset = (nchans - 1) * nbytes # Size channel = 2
            step   = nchans * nbytes
            ONE    = pack( TYPE , OPAQUE      )
            ZERO   = pack( TYPE , TRANSPARENT )
            writer = memoryview( rawdata ).cast( 'B' )
            # TODO: Test this, I think it would fail
            length = rlength
            for i in range(alength):
                index = offset + i * step
                writer[index:index+step] = ZERO if reader[i] == TRANSPARENT else ONE
            writer.release()
        else:
            # TODO: Optimize, it has bad performance
            offset = nchans - 1
            step   = nchans
            writer = memoryview( rawdata ).cast( TYPE )
            for i in range(alength):
                writer[offset+i*step] = TRANSPARENT if reader[i] == TRANSPARENT else OPAQUE
            writer.release()
        return rawdata

    # TODO: Fix this, Kiki laughts everytime I try to solve a problem with her...
    @classmethod
    def __lift_to_alpha_channel_context__( cls , bytedata , size , depth ):
        CONTEXT     = DEPTHS[depth]
        TYPE        = CONTEXT[0]
        OPAQUE      = CONTEXT[1]
        TSIZE       = CONTEXT[2]
        TRANSPARENT = 0

        # TODO: Change this!, Krita uses 4 bytes for channels!
        #       What can I do?, if depth is Float, then write as 'f' float32
        #       if is unsigned, then write as unsigned int32
        rsize = size * TSIZE
        result = bytearray( rsize )
        reader = memoryview( bytedata ).cast( 'B' )
        if TYPE == 'e':  # half-float
            # Result byte size. Used for manually cast.
            step  = 2
            ONE   = pack( TYPE , OPAQUE      )
            ZERO  = pack( TYPE , TRANSPARENT )
            writer = memoryview( result   ).cast( 'B' )
            for i in range(0,rsize,step):
                writer[i:i+step] = ZERO if reader[i] == TRANSPARENT else ONE
        else:
            writer = memoryview( result   ).cast( TYPE )
            for i in range(size):
                # TODO: Delete print
                print( f"readed[{i}] -> {reader[i]}" )
                writer[i] = TRANSPARENT if reader[i] == TRANSPARENT else OPAQUE
        return result

    # TODO: Write directly into the channel instead writting into the node pixel data
    def writeAlpha( self , node , bytedata , size , bounds ):
        """ opaque :: Number """
        alpha_channel   = node.channels()[-1]
        data_in_context = Writer.__lift_to_alpha_channel_context__( bytedata          ,
                                                                    size              ,
                                                                    node.colorDepth() )
        print( f"IN CONTEXT: {data_in_context}")
        alpha_channel.setPixelData( data_in_context , bounds )
