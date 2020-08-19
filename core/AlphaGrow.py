# Module:      core.AlphaGrow.py | [ Language Python ]
# Created by: ( Gaps | sGaps | ArtGaps )
# ----------------------------------------------------
TYPES = { 1 : "B" ,
          2 : "H" ,
          4 : "I" ,
          8 : "L" }
class Grow( object ):
    # TODO: Add a better description
    # TODO: Write about both indices arrays.
    """ Utility object that takes a raw data where each element has the value of 0x00 or 0xFF, and transform each
        to a bit field [$Grow-Data]. This is used to model how the opaque can grow using different methods.

        The bits of a [$Pixel-Enviroment] bit field can be readed as:
            bit 7:  Has a neighbor at West  [W]
            bit 6:  Has a neighbor at North [N]
            bit 5:  Has a neighbor at South [S]
            bit 4:  Has a neighbor at East  [E]
            bit 3:  Not used                [-]
            bit 2:  Not used                [-]
            bit 1:  Not used                [-]
            bit 0:  Not used                [-]
        Or in horizontal representation
            ==>     76543210    bits            $Pixel-Enviroment
                    WNSE----    value

        The bits of a [$Grow-State] bit field can be readed as:
            bit 7:  Can grow to West    [W]
            bit 6:  Can grow to North   [N]
            bit 5:  Can grow to South   [S]
            bit 4:  Can grow to East    [E]
        -   bit 3:  Has been Explored   [!] <- Deprecated
            bit 2:  Search Request      [$]
            bit 1:  Not used            [-]
            bit 0:  Is Opaque           [O]
        Or in horizontal representation
            ==>     76543210    bits
                    WNSE!$-O    value
        Use unlift_data to get a sequence that can be used in the external world.
    """
    # TODO: Optimize!!
    # Pass the size of the [GRect]
    # TODO: Delete old_mode         -------------------------------\
    def __init__( self , data , width , size , safe_mode = True , old_mode = False ):
        """ Save shared information for futher method applications. """
        # TODO: Finish

        self.data         = None
        self.size         = None
        self.width        = None
        # TODO: See if is really required use __searchBody in this object.
        self.__states     = None
        self.__searchView = None
        self.__nextView   = None    # TODO: Watch this.
        self.__indexSize  = None    # TODO: Consider remove it. I think you can use __searchView.itemsize instead.
        self.__count      = None
        self.safemode     = None

        # TODO: Delete old_mode --------------------------\
        self.setData( data , width , size , safe_mode , old_mode )
    @classmethod
    def singleton( cls ):
        return cls( None , 0 , 0 , False )

    # __get_required_bytes_for__ :: (Bounded a , Integral a) => a -> Int
    @classmethod
    def __get_required_bytes_for__( cls , size ):
        """ See How many bytes are required to represent size :: Int """
        limit = 1 << 8
        for k in TYPES:
            if size < limit: return k
            else:            limit <<= 8
        raise TypeError( f"Size uses too many bytes. Available bytes sizes: {set(TYPES.keys())}" )

    # TODO: Delete old_mode --------------------------------------\
    def setData( self , data , width , size , safe_mode = True , old_mode = False ):
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
        self.size     = size

        self.__indexSize   = Grow.__get_required_bytes_for__( size )
        required_size      = size * self.__indexSize
        self.__environment = bytearray( required_size )   # TODO: Look if this is right
        # Verify if is totally required create a new __searchBody array
        if not self.__searchView or len( previous ) != size:
            # Cast the search body into a integer of the required sizes to represent the size value.
            self.__searchView = memoryview( bytearray(required_size) ).cast( TYPES[self.__indexSize] )
            self.__nextView   = memoryview( bytearray(required_size) ).cast( TYPES[self.__indexSize] )
        # Always resets the count of indexes.
        self.__count = 0
        # Lift the information to the [$Grow-Data] context.

        # TODO: Delete old_mode -\
        if old_mode:
            self.__lift_to_context__()
        else:
            self.__lift_to_search_context__()


    #DEPRECATED:
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
        # BEWARE
        self.__count = count
        # Update the search variable:

    def __lift_to_search_context__( self ):
        """ Add elements to search context. Doesn't modify any bits.
            NOTE: It's O(n**2). This doesn't modify any bit in the contained data.
                  It only adds the indices which are part of the singleton border
                  of the layer. 

            NOTE: This method ensures that only transparent pixels are added into the search list. """
        search = self.__searchView
        count  = 0

        rawlength = self.size
        rows      = self.width
        first_row = rows
        last_row  = rawlength - rows
        last_col  = rows - 1

        data      = self.data
        for pos in range(rawlength):
            pixel = data[pos]
            # Hard coded "Any neighbor" addition policy:
            if not pixel and (  (pos > first_row       and data[pos - rows]) or     # Has a opaque neighbor at north.
                                (pos < last_row        and data[pos + rows]) or     # ::     ::      ::     at south.
                                (pos % rows            and data[pos - 1])    or     # ::     ::      ::     at west.
                                (pos % rows < last_col and data[pos + 1])    ):     # ::     ::      ::     at east.
                search[count] = pos
                count        += 1
        # Count update.
        self.__count = count

    def __any_neighbor_policy__( self , environment ):
        """ __any_neighbor_policy__ :: [$Pixel-Enviroment] -> e | e = 0 , 1
            State must be a [$Pixel-Enviroment] bit field.
            It has a neighbor if the high nibble has a enabled bit. """
        return environment & 0xF0

    def __is_corner_policy__( self , environment ):
        """ One of these bits enabled means there's free space at the respectively direction.
            WEST  = 1 << 7  = 0x80
            NORTH = 1 << 6  = 0x40
            SOUTH = 1 << 5  = 0x20
            EAST  = 1 << 4  = 0x10 """
        h  = 1 if environment & 0x80 else 0
        h += 1 if environment & 0x10 else 0
        if h != 1: return 0x00
        v  = 1 if environment & 0x40 else 0
        v += 1 if environment & 0x20 else 0
        return 0x01 if h == v else 0x00

    def __not_corner_policy__( self , environment ):
        return not self.__is_corner_policy__( environment )

    def __always_grow_policy__( self , _ ):
        return 0x01

    # TODO: Add a better description.
    def __run_automata__( self , grow_policy ):
        """ Runs a grow policy inside the object. It must be an function that takes
            an [$Pixel-Enviroment] and returns a Bool object (or something that could
            apply cast into bool). """
        newcount    = 0
        count       = self.__count
        search      = self.__searchView
        newsearch   = self.__nextView
        
        states      = self.data          # Data + context = states.
        environment = self.__environment # Enviroment = Data + lookup

        rows      = self.width
        first_row = rows
        last_row  = self.size - rows
        last_col  = rows - 1

        # Common
        WEST     = 1 << 7   # [W]
        NORTH    = 1 << 6   # [N]
        SOUTH    = 1 << 5   # [S]
        EAST     = 1 << 4   # [E]

        # For states:
        EXPLORED = 1 << 3   # [!]
        SEARCHRQ = 1 << 2   # [$]
        OPAQUE   = 1        # [O]

        # TODO: Optimize!
        for record in range(count):
            pos     = search[record]
            env     = environment[pos]
            state   = states[pos]
            if not state & EXPLORED:
                # Lift to context: register if it can grow to a specific direction.
                if pos > first_row:
                    lookup = states[pos - rows]
                    if lookup & OPAQUE:
                        env |= NORTH                        # Has a opaque n. at north.
                    elif not lookup & SEARCHRQ: 
                        state              |= NORTH         # free space at north.
                        states[pos - rows] |= SEARCHRQ      # Search request to north.

                if pos < last_row:
                    lookup = states[pos + rows]
                    if lookup & OPAQUE:
                        env |= SOUTH                        # Has a opaque n. at south.
                    elif not lookup & SEARCHRQ:
                        state              |= SOUTH         # free space at south.
                        states[pos + rows] |= SEARCHRQ      # That block is reserved now

                if pos % rows:
                    lookup = states[pos - 1]
                    if lookup & OPAQUE:
                        env |= WEST                         # Has a opaque n. at west.
                    elif not lookup & SEARCHRQ:
                        state           |= WEST             # free space at west.
                        states[pos - 1] |= SEARCHRQ         # That block is reserved now

                if pos % rows < last_col:
                    lookup = states[pos + 1]
                    if lookup & OPAQUE:
                        env |= EAST                         # Has a opaque n. at east.
                    elif not lookup & SEARCHRQ:
                        state           |= EAST             # free space at east.
                        states[pos + 1] |= SEARCHRQ         # That block is reserved now
                # Force write:
                state           |= EXPLORED
                states[pos]      = state
                environment[pos] = env

            # We have explored the current position, so we only have to know if with
            # the given current state, we can consider this pixel as opaque.
            if grow_policy( env ):
                states[pos] |= OPAQUE
                # search list)
                if state & NORTH:
                    newsearch[newcount] = pos - rows
                    newcount           += 1

                if state & SOUTH:
                    newsearch[newcount] = pos + rows
                    newcount           += 1

                if state & WEST:
                    newsearch[newcount] = pos - 1
                    newcount           += 1

                if state & EAST:
                    newsearch[newcount] = pos + 1
                    newcount           += 1
            else:
                # If it has not been written, then we must wait until it can grow.
                # that means: we add it to the next search.
                newsearch[newcount] = pos
                newcount           += 1
        # Update search:
        self.__count = newcount 
        self.__searchView , self.__nextView = self.__nextView , self.__searchView

    def force_grow( self ):
        self.__run_automata__( self.__always_grow_policy__ )

    def any_neighbor_grow( self ):
        self.__run_automata__( self.__any_neighbor_policy__ )

    def corners_grow( self ):
        self.__run_automata__( self.__is_corner_policy__ )

    def not_corners_grow( self ):
        self.__run_automata__( self.__not_corner_policy__ )

    def grow_with_custom_policy( self , grow_policy ):
        """ grow_policy :: ($Pixel-Environment -> Bool) -> None """
        self.__run_automata__( grow_policy )

    #DEPRECATED:
    def __any_neighbor__( self , pixel ):
        """ pixel must be an int8. where its bits have the folowing meaning:
                7864    3                   21          0
                WNSE    has_been_written    not used    is_opaque

            returns true if the pixel can grow to any direction W | N | S | E == True
        """
        return pixel & 0xF0 # If any dir is enabled

    #DEPRECATED:
    def __always_grow__( self , pixel ):
        """ pixel must be an int8. where its bits have the folowing meaning:
                7864    3                   21          0
                WNSE    has_been_written    not used    is_opaque

            Always returns "true"
        """
        return True

    #DEPRECATED:
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

    #DEPRECATED:
    def grow_if_any_neighbor( self ):
        self.__grow__( self.__any_neighbor__ )

    #DEPRECATED:
    # TODO: Rename to grow_in_diagonal
    def grow_if_is_corner( self ):
        self.__grow__( self.__is_corner__ )

    #DEPRECATED:
    # TODO: Rename to if grow_to_all_directions
    def grow_always( self ):
        self.__grow__( self.__always_grow__ )

    #DEPRECATED:
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
        count     = self.__count
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
        self.__count = nextcount
        # SWAP()
        self.__searchView , self.__nextView = self.__nextView , self.__searchView

    # TODO: Optimize!
    def unlift_data( self ):
        """ Returns a new data without the [$Grow-Data] bit field context. The returned data can be used
            in the RealWorld. """
        return bytearray( 0xFF if p & 0x01 else 0x00 for p in self.data )

    # TODO: Optimize!
    def difference_with( self , external ):
        d = self.data
        return bytearray( 0xFF & ~external[i] if d[i] & 0x01 else 0x00 & ~external[i] for i in range(self.size) )

    def xor_with( self , external ):
        """ Returns a new data without the [$Grow-Data] bit field context, then apply XOR operation with a give 'external'
            data. It's used for make easier a bit more efficient this difference operation. """
        # Unlift the Grow context and apply XOR
        d = self.data
        return bytearray( external[i] ^ 0xFF if d[i] & 0x01 else external[i] ^ 0x00 for i in range(self.size) )


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
