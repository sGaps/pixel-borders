# Module:      AlphaGrow.py | [ Language Python ]
# Created by: ( Gaps | sGaps | ArtGaps )
# ---------------------------------------------------
class Grow( object ):
    def __init__( self , data , width , secure_mode = True ):
        # Ensures this class doesn't modify nothing from outside...
        # And doesn't copy nothing if the user is totally sure about
        # what's doing.
        if secure_mode:
            self.data = data.copy()
        else:
            self.data = data
        self.size  = len( data )
        self.clone = bytearray( self.size )
        self.w     = width

    def classic_cross( self , i , data , width , size , opaque = 0xFF , transparent = 0x0 ):
        """             Grow Criteria:
            (.) = ignored box       |       . x .
            (x) = lookup box        |       x * x
            (*) = current box       |       . x .
            if some x != alpha, then return opaque value, else return transparent.
        """
        if data[i] != transparent:
            return opaque

        north  = i - width
        south  = i + width
        east   = i + 1
        west   = i - 1

        if(  ( north     >  0         and data[north] != transparent ) or       # Has north and is it opaque?
             ( south     <  size      and data[south] != transparent ) or       # Has south and is it opaque?
             ( i % width != width - 1 and data[east]  != transparent ) or       # Has east  and is it opaque?
             ( i % width != 0         and data[west]  != transparent )  ):      # Has west  and is it opaque?
            return opaque
        else:
            return transparent

    def corner_lookup( self , i , data , width , size , opaque = 0xFF , transparent = 0x0 ):
        """             Grow Criteria:
            (.) = ignored box                       |       . v .
            (h) = horizontal box                    |       h * h
            (v) = vertical box                      |       . v .
            (*) = current box (it's seen too)
            if the number of vertical and horizontal boxes are equal and the * isn't alpha, return opaque. Else return transparent.
        """
        if data[i] == transparent:
            return transparent

        north = i - width
        south = i + width
        east  = i + 1
        west  = i - 1
        # Vertical constraint:
        v     = 1 if north > 0    and data[north] != transparent else 0           # Count north
        v    += 1 if south < size and data[south] != transparent else 0           # Count south

        # Horizontal constraint:
        h    = 1 if i % width != width - 1 and data[east] != transparent else 0   # Count east
        h   += 1 if i % width != 0         and data[west] != transparent else 0   # Count west

        return v == 1 and v == h


    # Pre: { len(mutable) == len(auxiliar) and size == len(mutable) }
    def __abstract_grow__( self , mutable , auxiliar , size  , width , criteria , opaque = 0xFF , transparent = 0x00 ):
        self.__clone_into__( mutable , auxiliar , size )
        for i in range( size ):
            mutable[i] = criteria( i , auxiliar , width , size , opaque , transparent )

    # Pre: { len(cloned) == len(source) }
    def __clone_into__( self , source , cloned , size ):
        for i in range( size ):
            cloned[i] = source[i]

    def classic_grow( self , opaque = 0xFF , transparent = 0x00 ):
        self.__abstract_grow__( self.data   , self.clone         , self.size , 
                                self.w      , self.classic_cross , opaque    ,
                                transparent )

    def corners_grow( self , opaque = 0xFF , transparent = 0x00 ):
        self.__abstract_grow__( self.data   , self.clone         , self.size , 
                                self.w      , self.classic_cross , opaque    ,
                                transparent )

    def get_unsafe_data( self ):
        return self.data

    def get_data( self ):
        return self.data.copy()

# -------------------------------------------------------------
# TODO: REMOVE THIS
if __name__ == "__main__":
    case = "Simple"
    if case == "Simple":
        b = bytearray( b"\x00\x00\x00" + 
                       b"\x00\xff\x00" +
                       b"\x00\x00\x00" )
        width  = 3
        secure = True
    else:
        b = bytearray()
        width  = 0
        secure = False

    g = Grow( b , width , secure )
    g.classic_grow()
    g.corners_grow()
# -------------------------------------------------------------
