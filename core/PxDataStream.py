# Module:      core.PxDataStream.py | [ Language Python ]
# Created by: ( Gaps | sGaps | ArtGaps )
# ------------------------------------------------------------
""" Extends the a QDataStream for get a better pixel data handle for
    krita nodes. This manages the type using a depth and a endianess. """
from PyQt5.QtCore import QDataStream , QByteArray , QBuffer
import struct

LittleEndian  = QDataStream.LittleEndian
BigEndian     = QDataStream.BigEndian
Float32       = QDataStream.SinglePrecision
Float64       = QDataStream.DoublePrecision
ReadMode      = QBuffer.ReadOnly
WriteMode     = QBuffer.WriteOnly
ReadWriteMode = QBuffer.ReadWrite
UInt  = "U"
Float = "F"

class ColorDepthException( Exception ):
    def __init__( self , args ):
        super().__init__( args )

class PxDataStream( QDataStream ):
    Big    = ">"
    Little = "<"
    empty  = b"\x00"
    def __init__( self , qbytearray , depth , streamMode = ReadMode , endian = LittleEndian , floatPrec = Float32 ):
        """ QDataStream Wrapper for read/write krita pixel data.
            NOTE #1:    this only supports sequential read/write.
            NOTE #2:    If you want to write information, then you must use
                        <>.startTransaction() for start to writing and
                        <>.commitTransaction() to finish. """
        super().__init__( qbytearray , streamMode )

        if endian == BigEndian:
            self.__endian_pattern__ = PxDataStream.Big
        else:
            self.__endian_pattern__ = PxDataStream.Little
        self.__half_pattern__ = self.__endian_pattern__ + "e"
        self.__half_force__   = self.__endian_pattern__ + "f"

        self.setByteOrder( endian )
        self.setFloatingPointPrecision( Float32 )
        self.__set_handle_methods__( depth )
        self.__last_info_readed__ = None

        # Dummy cast_method:
        self.__cast_method__  = lambda x: x
        self.__fill_pattern__ = b""

    # TODO: Verify if this method family is deprecated:
    #       { force_write , set_force_write_policy__ , local_force_write , __dummy_promote_little__ ,
    #         __dummy_promote_big__ , __select_force_write_method__ , ... }
    # TODO: VERIFY [BEGIN] {#1}
    def force_write( self , value ):
        """ Force to write the literal bytes of a value into the object as a
            value.
            This uses the valueDepth setted using .set_cast_write_config(...) """
        self.__force_write__( value )

    def set_force_write_policy__( self , valueDepth ):
        """ This sets the valueDepth of incoming external data used by .cast_and_write(...)
            It's useful when you're trying to cast & write multiple values. """
        self.__force_write__ = self.__select_force_write_method__( valueDepth )

    def local_force_write( self , value , valueDepth ):
        """ Cast/Promote a value of the type of the data contained in the buffer.
            Then write the value if writting is enabled.
            this uses valueDepth to specify the format of the origin value.
            value       :: Number
            valueDepth  :: String
                where valueDepth = (Fd)|(Ud) and d :: Int """
        write = self.__select_force_write_method__( valueDepth )
        write( value )

    # TODO: Verify if this works:
    def __dummy_promote_little__( self , value ):
        self.__writeM__( value )
        self.writeRawData( self.__fill_pattern__ )

    def __dummy_promote_big__( self , value ):
        self.writeRawData( self.__fill_pattern__ )
        self.__writeM__( value )

    def __select_force_write_method__( self , valueDepth ):
        try:
            valType  = valueDepth[0]
            valSizeB = int( valueDepth[1:] ) // 8
        except:
            return lambda x: ()             # if something goes wrong, returns Bottom _|_

        if valSizeB <= self.__sizeVB__:
            # Promote actions
            self.__fill_pattern__ = (self.__sizeVB__ - valSizeB)*PxDataStream.empty
            if self.__endian_pattern__ == PxDataStream.Little:
                return self.__dummy_promote_little__
            else:
                return self.__dummy_promote_big__
        else:
            # Cast actions:
            if self.__depthV__ == UInt:
                return __write_as__int__
            elif self.__depthV__ == Float:
                if valType == UInt:
                    return self.__write_as__float__
                elif self.__sizeVB__*8 == 16:
                    if self.__endian_pattern__ == PxDataStream.Little:
                        return self.__write_float32_as_float16_little__
                    else:
                        return self.__write_float32_as_float16_big__
                else:
                    return self.__write_float32_as_float16__

    def __write_as__int__( self , value ):
        self.writeValue( int( value ) % 2**self.__sizeVB__ )

    # TODO: Verify if this works fine.
    def __write_float32_as_float16_little__( self , value ):
        components = struct.pack( self.__half_force__ , float(value) )
        self.writeValue( struct.unpack( self.__half_pattern__ , components[0] ) )
        self.writeValue( struct.unpack( self.__half_pattern__ , components[1] ) )

    # TODO: Verify if this works fine.
    def __write_float32_as_float16__big__( self , value ):
        components = struct.pack( self.__half_force__ , float(value) )
        self.writeValue( struct.unpack( self.__half_pattern__ , components[0] ) )
        self.writeValue( struct.unpack( self.__half_pattern__ , components[1] ) )

    # NOTE: This will fail for F32 -> F16
    def __write_as__float__( self , value ):
        self.writeValue( float( value ) )
    # TODO: VERIFY [END] {#1}

    def ignoreValue( self ):
        """ Skips the read/write function of a value """
        self.skipRawData( self.__sizeVB__ )

    def writeValue( self , value ):
        """ Write and a managed value from buffer. """
        self.__writeM__( value )

    def readValue( self ):
        """ Read and return a managed value from buffer. """
        return self.__readM__()

    def __half_read__( self ):
        """ Reads a Float16 value """
        # Reads a Float16-sized bytes
        block = self.readRawData( self.__sizeVB__ )
        return struct.unpack( self.__half_pattern__ , block )[0] # [0] because unpack returns a tuple

    def __half_write__( self , value ):
        """ Writes a Float16 value """
        block = struct.pack( self.__half_pattern__ , value )
        self.writeRawData( block )

    def __set_handle_methods__( self , depth ):
        try:
            sizeDepth = int( depth[1:] )
        except:
            sizeDepth = 8
        typeDepth       = depth[0]
        self.__depthV__ = typeDepth
        if typeDepth == UInt:
            if sizeDepth == 8:
                # Read-Write:
                self.__readM__  = self.readUInt8
                self.__writeM__ = self.writeUInt8
                # Cast:
            elif sizeDepth == 16:
                # Read-Write:
                self.__readM__  = self.readUInt16
                self.__writeM__ = self.writeUInt16
                # Cast:
            else:
                raise ColorDepthException( f"Unknow depth passed as argument: {depth}" )
            self.__sizeVB__ = sizeDepth // 8    # size of value in bytes
        elif typeDepth == Float:
            if sizeDepth == 16:
                # NOTE: This needs a special treats:
                # Read-Write:
                self.__readM__  = self.__half_read__
                self.__writeM__ = self.__half_write__
            elif sizeDepth == 32:
                self.__readM__  = self.readFloat
                self.__writeM__ = self.writeFloat
            else:
                raise ColorDepthException( f"Unknow depth passed as argument: {depth}" )
            self.__sizeVB__ = sizeDepth // 8    # size of value in bytes



