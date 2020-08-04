# Module:      core.AlphaGrow.py | [ Language Python ]
# Created by: ( Gaps | sGaps | ArtGaps )
# ----------------------------------------------------
""" Defines a Grow object. This is a service that can
    be used to make grow opaque values in a bytearray
    corresponding to the pixel data of a node. """
class Grow( object ):
    """ Service class to make grow values using few criterias.
        NOTE: this modifies the data passed to the methods if
              safe mode isn't enabled.
              Also, data must be mutable. """
    def __init__( self , size , width , safe_mode = True ):
        """ Save shared information for futher method applications. """
        # Ensures this class doesn't modify nothing from outside...
        # And doesn't copy nothing if the user is totally sure about
        # what's doing.
        self.size = size
        self.w    = width
        self.aux  = bytearray(size)
        self.safe = safe_mode

    def setSize( self , size ):
        self.size = size
    def setWidth( self , width ):
        self.width = width
    def setSafemode( self , mode = True ):
        self.safe = mode

    def classic_cross( self , i , data , width , size , opaque = 0xFF , transparent = 0x0 ):
        """ [ GROW METHOD ]
                                Criteria:
            (.) = ignored box       |       . x .
            (x) = lookup box        |       x * x
            (*) = current box       |       . x .
            if some x != alpha, then return opaque value, else return transparent.
        """
        # Ensures the opaque aren't totally modified
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

    # TODO: Fix. It's broken
    def corner_lookup( self , i , data , width , size , opaque = 0xFF , transparent = 0x0 ):
        """ [ GROW METHOD ]
                                Criteria:
            (.) = ignored box                       |       . v .
            (h) = horizontal box                    |       h * h
            (v) = vertical box                      |       . v .
            (*) = current box (it's seen too)
            if the number of vertical and horizontal boxes are equal and the * isn't alpha, return opaque. Else return transparent.
        """
        # Ensures the opaque aren't totally modified
        if data[i] != transparent:
            return opaque

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
        if v == 1 and v == h:
            return opaque
        else:
            return transparent

    # Pre: { len(mutable) == len(auxiliar) and size == len(mutable) }
    def __abstract_grow__( self , mutable , auxiliar , size  , width , criteria , opaque = 0xFF , transparent = 0x00 ):
        """ Make a safe copy in-place of the mutable object into auxiliar object
            and applies a criteria to every object of the mutable object. """
        auxiliar[:] = mutable
        for i in range( size ):
            mutable[i] = criteria( i , auxiliar , width , size , opaque , transparent )

    # Pre: { len(cloned) == len(source) }
    def __clone_into__( self , source , cloned , size ):
        """ Make a safe copy in-place of the source object into cloned object. """
        cloned[:] = source

    def classic_grow( self , data , opaque = 0xFF , transparent = 0x00 ):
        """ Apply classic_cross method to data and returns it as result. """
        return self.repeated_classic_grow( data , 1 , opaque , transparent )

    def corners_grow( self , data , opaque = 0xFF , transparent = 0x00 ):
        """ Apply corner_lookup method to data and returns it as result. """
        return self.repeated_corners_grow( data , 1 , opaque , transparent )

    def repeated_classic_grow( self , data , repeat = 1 , opaque = 0xFF , transparent = 0x00 ):
        """ Apply classic_cross method 'repeat' times to data and returns it as result. """
        if self.safe: target = data.copy()
        else:         target = data
        for steps in range(repeat):
            self.__abstract_grow__( target      , self.aux           , self.size , 
                                    self.w      , self.classic_cross , opaque    ,
                                    transparent )
        return target

    def repeated_corners_grow( self , data , repeat = 1 , opaque = 0xFF , transparent = 0x00 ):
        """ Apply corner_lookup method 'repeat' times to data and returns it as result. """
        if self.safe: target = data.copy()
        else:         target = data
        for steps in range(repeat):
            self.__abstract_grow__( target      , self.aux           , self.size , 
                                    self.w      , self.corner_lookup , opaque    ,
                                    transparent )
        return target

# -------------------------------------------------------------
if __name__ == "__main__":
    case = "unsafe"
    if case == "secure":
        b = bytearray( b"\x00\x00\x00" + 
                       b"\x00\xff\x00" +
                       b"\x00\x00\x00" )
        width  = 3
        secure = True
    elif case == "unsafe":
        b = bytearray( b"\x00\x00\x00" + 
                       b"\x00\xff\x00" +
                       b"\x00\x00\x00" )
        width  = 3
        secure = False
    else:
        b = bytearray()
        width  = 0
        secure = False

    g  = Grow( len(b) , width , secure )
    b1 = g.classic_grow(b)
    b2 = g.corners_grow(b)
    print( "Original" , b  , id(b)  )
    print( "Classic " , b1 , id(b1) )
    print( "Corners " , b2 , id(b2) )
# -------------------------------------------------------------
