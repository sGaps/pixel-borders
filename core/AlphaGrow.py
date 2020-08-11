# Module:      core.AlphaGrow.py | [ Language Python ]
# Created by: ( Gaps | sGaps | ArtGaps )
# ----------------------------------------------------
TYPES = { 1 : "B" ,
          2 : "H" ,
          4 : "I" ,
          8 : "L" }
class Grow( object ):
    """ Utility object that takes a raw data where each element has the value of 0x00 or 0xFF, and transform each
        to a bit field [$Grow-Data]. This is used to model how the opaque can grow using different methods.

        The bits of a [$Grow-Data] bit field can be readed as:
            bit 7:  West                [W]
            bit 6:  North               [N]
            bit 5:  South               [S]
            bit 4:  East                [E]
            bit 3:  Has been Written    [*]
            bit 2:  Not used            [-]
            bit 1:  Not used            [-]
            bit 0:  Is Opaque           [O]
        Or in horizontal representation
            ==>     76543210    bits
                    WNSE*--0    value

        Use unlift_data to get a sequence that can be used in the external world.
    """
    # TODO: Optimize!!
    # Pass the size of the [GRect]
    def __init__( self , data , width , size , safe_mode = True ):
        """ Save shared information for futher method applications. """
        # TODO: Finish

        self.data         = None
        self.size         = None
        self.width        = None
        # TODO: See if is really required use __searchBody in this object.
        self.__searchBody = None
        self.__searchView = None
        self.__nextView   = None    # TODO: Watch this.
        self.__indexSize  = None    # TODO: Consider remove it. I think you can use __searchView.itemsize instead.
        self.__count      = None
        self.safemode     = None
        self.setData( data , width , size , safe_mode )

    # __get_required_bytes_for__ :: (Bounded a , Integral a) => a -> Int
    @classmethod
    def __get_required_bytes_for__( cls , size ):
        """ See How many bytes are required to represent size :: Int """
        limit = 1 << 8
        for k in TYPES:
            if size < limit: return k
            else:            limit <<= 8
        raise TypeError( f"Size uses too many bytes. Available bytes sizes: {set(TYPES.keys())}" )

    def setData( self , data , width , size , safe_mode = True ):
        """ Smart constructor/Setter. If safe_mode is False, then data will be mutated after every operation
            of the object. """
        # Data selection:
        if safe_mode:
            self.data = data.copy()
        else:
            if data is not self.data:
                self.data = data
        # Always is updated
        self.width    = width
        self.safemode = safe_mode
        self.size = size

        # Verify if is totally required create a new __searchBody array
        if not self.__searchBody or len( self.__searchBody ) != size:
            self.__indexSize  = Grow.__get_required_bytes_for__( size )
            self.__searchBody = bytearray( size * self.__indexSize )
            # TODO: remove __searchBody and make the bytearray build into the memoryview as I did in the __nextView
            # Cast the search body into a integer of the required sizes to represent the size value.
            self.__searchView = memoryview( self.__searchBody ).cast( TYPES[self.__indexSize] )
            self.__nextView   = memoryview( bytearray(size * self.__indexSize ) ).cast( TYPES[self.__indexSize] )
        # Always resets the count of indexes.
        self.__count = 0
        # Lift the information to the [$Grow-Data] context.
        self.__lift_to_context__()

    def __lift_to_context__( self ):
        """ It takes a raw data in self.data to transform it into a [$Grow-Data] sequence.
            Also adds to a seach list these transparent pixels that have some opaque neighbors.

            NOTE: This is the bottleneck of this object. It has a O(n**2) complexity because
                  it must to iterate over the whole raw data to determine which would be explored
                  in the future. So, try not use this if it
        """
        # local variables are faster
        # TODO: Declare 1 << 7 , 1 << 6 ... values as Global variables, then copy them locally.
        IS_OPAQUE = 1           # Used as mask. Is the pixel opaque?
        WRITTEN   = 1 << 3      # Used as mask. Does the pixel has been written? ***
        ENABLEALL = 0xF0
        WEST     = 1 << 7
        NORTH    = 1 << 6
        SOUTH    = 1 << 5
        EAST     = 1 << 4

        NOTNORTH = ~NORTH
        NOTSOUTH = ~SOUTH
        NOTWEST  = ~WEST
        NOTEAST  = ~EAST

        data  = self.data
        size  = self.size
        width = self.width
        search = self.__searchView
        count = self.__count

        for pos in range(size):
            pixel = data[pos]
            if pixel & IS_OPAQUE:       # Lookup to the Opaque component
                data[pos] = IS_OPAQUE   # Doesn't grow to any direction
            else:
                # Enable all directions lookups
                pixel |= ENABLEALL

                # Cache some values:
                north  = pos - width
                south  = pos + width
                east   = pos + 1
                west   = pos - 1

                # if has north and is opaque in north, then the pixel only can't grow to north.
                if north > 0        and data[north] & IS_OPAQUE:
                    pixel = ( pixel & NOTNORTH ) | WRITTEN     # Disable North, mark the pixel as written

                if south < size     and data[south] & IS_OPAQUE:
                    pixel = ( pixel & NOTSOUTH ) | WRITTEN     # Disable South, mark the pixel as written

                if pos % width  and data[west]  & IS_OPAQUE:
                    pixel = ( pixel & NOTWEST  ) | WRITTEN     # Disable West , mark the pixel as written
                    
                if pos % width != width - 1 and data[east] & IS_OPAQUE:
                    pixel = ( pixel & NOTEAST  ) | WRITTEN     # Disable East , mark the pixel as written

                # Only adds these transparent pixels to the search.
                if pixel & WRITTEN:
                    # Add to the search:
                    data[pos]     = pixel
                    search[count] = pos
                    count        += 1
        # Update the number of elements:
        self.count = count
        # Update the search variable:

    def __any_neighbor__( self , pixel ):
        """ pixel must be an int8. where its bits have the folowing meaning:
                7864    3                   21          0
                WNSE    has_been_written    not used    is_opaque

            returns true if the pixel can grow to any direction W | N | S | E == True
        """
        return pixel & 0xF0 # If any dir is enabled

    def __always_grow__( self , pixel ):
        """ pixel must be an int8. where its bits have the folowing meaning:
                7864    3                   21          0
                WNSE    has_been_written    not used    is_opaque

            Always returns "true"
        """
        return True

    # TODO: Fix, It grows to <- and ->
    def __is_corner__( self , pixel ):
        """ pixel must be an int8. where its bits have the folowing meaning:
                7864    3                   21          0
                WNSE    has_been_written    not used    is_opaque
            returns ture if the number of vertical neighbors and horizontal neighbors are equal to 1.
            WEST  = 1 << 7  = 0x80
            NORTH = 1 << 6  = 0x40
            SOUTH = 1 << 5  = 0x20
            EAST  = 1 << 4  = 0x10
        """
        h  = 1 if pixel & 0x80 else 0   # West
        h += 1 if pixel & 0x10 else 0   # East
        if h != 1: return False
        v  = 1 if pixel & 0x40 else 0   # North
        v += 1 if pixel & 0x20 else 0   # South
        return h == v

    def grow_if_any_neighbor( self ):
        self.__grow__( self.__any_neighbor__ )

    # TODO: Rename to grow_in_diagonal
    def grow_if_is_corner( self ):
        self.__grow__( self.__is_corner__ )

    # TODO: Rename to if grow_to_all_directions
    def grow_always( self ):
        self.__grow__( self.__always_grow__ )

    # TODO: add selection
    def __grow__( self , grow_condition ):
        """ I think pattern must be a function
            pattern must be an int8 with the relevant grow rules following the next
            Bits meanings:  7654    3                    21         0    
                            WNSE    has_been_written     not_used   is_opaque
        """
        # TODO: Declare 1 << 7 , 1 << 6 ... values as Global variables, then copy them locally.
        IS_OPAQUE = 1           # Used as mask. Is the pixel opaque?
        WRITTEN   = 1 << 3      # Used as mask. Does the pixel has been written? ***
        ENABLEALL = 0xF0
        WEST     = 1 << 7
        NORTH    = 1 << 6
        SOUTH    = 1 << 5
        EAST     = 1 << 4

        NOTNORTH = ~NORTH
        NOTSOUTH = ~SOUTH
        NOTWEST  = ~WEST
        NOTEAST  = ~EAST

        data   = self.data
        size   = self.size
        width  = self.width
        currsearch = self.__searchView
        nextsearch = self.__nextView
        count     = self.count
        nextcount = 0

        # Only do lookup into the currsearch 'array'
        for index in range(count):
            pos   = currsearch[index]
            pixel = data[pos]
            if not pixel & IS_OPAQUE:

                if grow_condition( pixel ):
                    data[pos] |= IS_OPAQUE

                # Cache some values:
                north  = pos - width
                south  = pos + width
                east   = pos + 1
                west   = pos - 1

                # if can grow to north and exists north, and also its north is opaque:
                if pixel & NORTH and north > 0 and not data[north] & IS_OPAQUE:
                    if not data[north] & WRITTEN:
                        data[north] |= ENABLEALL | WRITTEN
                        nextsearch[nextcount] = north
                        nextcount            += 1
                    # Disable South if it was enabled.
                    data[north] &= NOTSOUTH

                if pixel & SOUTH and south < size and not data[south] & IS_OPAQUE:
                    if not data[south] & WRITTEN:
                        data[south] |= ENABLEALL | WRITTEN
                        nextsearch[nextcount] = south
                        nextcount            += 1
                    # Disable South, mark the south pixel as written.
                    data[south] &= NOTNORTH

                if pos % width and not data[west] & IS_OPAQUE:
                    if not data[west] & WRITTEN:
                        data[west] |= ENABLEALL | WRITTEN
                        nextsearch[nextcount] = west
                        nextcount            += 1
                    # Disable West , mark the west pixel as written
                    data[west] &= NOTWEST
                    
                if pos % width != width - 1 and not data[east] & IS_OPAQUE:
                    if not data[east] & WRITTEN:
                        data[east] |= ENABLEALL | WRITTEN
                        nextsearch[nextcount] = east
                        nextcount            += 1
                    # Disable East , mark the pixel as written
                    data[east] &= NOTEAST
                
        # Update the number of elements:
        self.count = nextcount
        # SWAP()
        self.__searchView , self.__nextView = self.__nextView , self.__searchView

    def unlift_data( self ):
        """ Returns a new data without the [$Grow-Data] bit field context. The returned data can be used
            in the RealWorld. """
        return bytearray( 0xFF if p & 0x01 else 0x00 for p in self.data )

    def difference_with( self , external ):
        """ Returns a new data without the [$Grow-Data] bit field context, then apply XOR operation with a give 'external'
            data. It's used for make easier a bit more efficient this difference operation. """
        # Unlift the Grow context and apply XOR
        d = self.data
        return bytearray( external[i] ^ 0xFF if d[i] & 0x01 else external[i] ^ 0x00 for i in range(size) )

    # @DEPRECATED:
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

    # @DEPRECATED:
    def corner_lookup( self , i , data , width , size , opaque = 0xFF , transparent = 0x0 ):
        """ [ GROW METHOD ]
                                Criteria:
            (.) = ignored box                       |       . v .
            (h) = horizontal box                    |       h * h
            (v) = vertical box                      |       . v .
            (*) = current box (it's seen too)
            if the number of vertical and horizontal boxes are equal and the * isn't alpha,
            return opaque. Else return transparent.
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

    # @DEPRECATED:
    # Pre: { len(mutable) == len(auxiliar) and size == len(mutable) }
    def __abstract_grow__( self , mutable , auxiliar , size  , width , criteria , opaque = 0xFF , transparent = 0x00 ):
        """ Make a safe copy in-place of the mutable object into auxiliar object
            and applies a criteria to every object of the mutable object. """
        auxiliar[:] = mutable
        for i in range( size ):
            mutable[i] = criteria( i , auxiliar , width , size , opaque , transparent )

    # @DEPRECATED:
    # Pre: { len(cloned) == len(source) }
    def __clone_into__( self , source , cloned , size ):
        """ Make a safe copy in-place of the source object into cloned object. """
        cloned[:] = source

    # @DEPRECATED:
    def classic_grow( self , data , opaque = 0xFF , transparent = 0x00 ):
        """ Apply classic_cross method to data and returns it as result. """
        return self.repeated_classic_grow( data , 1 , opaque , transparent )

    # @DEPRECATED:
    def corners_grow( self , data , opaque = 0xFF , transparent = 0x00 ):
        """ Apply corner_lookup method to data and returns it as result. """
        return self.repeated_corners_grow( data , 1 , opaque , transparent )

    # @DEPRECATED:
    def repeated_classic_grow( self , data , repeat = 1 , opaque = 0xFF , transparent = 0x00 ):
        """ Apply classic_cross method 'repeat' times to data and returns it as result. """
        if self.safe: target = data.copy()
        else:         target = data
        for steps in range(repeat):
            self.__abstract_grow__( target      , self.aux           , self.size , 
                                    self.w      , self.classic_cross , opaque    ,
                                    transparent )
        return target

    # @DEPRECATED:
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
