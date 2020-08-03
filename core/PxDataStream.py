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

        self.setByteOrder( endian )
        self.setFloatingPointPrecision( Float32 )
        self.__set_handle_methods__( depth )
        self.__last_info_readed__ = None

        self.__cast_method__ = lambda x: ()

    def cast_and_write( self , value ):
        """ Cast/Promote a value of the type of the data contained in the buffer.
            Then write the value if writting is enabled. """
        pass

    def set_cast_write_config( self , valueDepth ):
        pass

    def local_cast_and_write( self , value , valueDepth ):
        pass

    def ignoreValue( self ):
        """ Skips the read/write function of a value """
        self.skipRawData( self.__sizeVB__ )

    def __ignore__half__( self ):
        """ Manual way to ignore data """
        if self.__current_half_index__ % 2 == 0:
            # BLOCK LOAD:
            block                        = self.readRawData( self.__sizeFloat32__ )
            self.__last_info_readed__    = struct.unpack( self.__half_read_pattern__ , block )
            value                        = self.__last_info_readed__[self.__current_half_index__]
            self.__current_half_index__ += 1
            return value
        else:
            value                        = self.__last_info_readed__[self.__current_half_index__]
            self.__current_half_index__ += 1
            return value

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
        typeDepth      = depth[0]
        self.__depth__ = typeDepth
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
            self.__sizeVB__ = sizeDepth // 8    # byte conversion
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
            self.__sizeVB__ = sizeDepth // 8    # byte conversion



