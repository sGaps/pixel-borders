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
            bit 3:  Next has neig. at West  [*W]
            bit 2:  Next has neig. at North [*N]
            bit 1:  Next has neig. at South [*S]
            bit 0:  Next has neig. at East  [*E]
        Or in horizontal representation
            ==>     76543210    bits            $Pixel-Enviroment
                    WNSE****    value
                        WNSE

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
    # TODO: Remove safe_mode flag. It's not used
    def __init__( self , data , width , size , safe_mode = True ):
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
        self.__prevSize   = 0
        self.safemode     = None

        self.setData( data , width , size , safe_mode )

    @classmethod
    def singleton( cls ):
        return cls( bytearray() , 0 , 0 , True )

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
    def setData( self , data , width , size , safe_mode = True ):
        """ Smart constructor/Setter. If safe_mode is False, then data will be mutated after every operation
            of the object. """
        self.data = bytearray( 0x01 if b else 0x00 for b in data )
        # it's Always updated
        self.width    = width
        self.safemode = safe_mode
        self.size     = size

        self.__indexSize   = Grow.__get_required_bytes_for__( size )
        required_size      = size * self.__indexSize
        self.__environment = bytearray( required_size )   # TODO: Look if this is right
        # Verify if is totally required create a new __searchBody array
        if not self.__searchView or len( self.__searchView ) != size:
            # Cast the search body into a integer of the required sizes to represent the size value.
            self.__searchView = memoryview( bytearray(required_size) ).cast( TYPES[self.__indexSize] )
            self.__nextView   = memoryview( bytearray(required_size) ).cast( TYPES[self.__indexSize] )
        # Always resets the count of indexes.
        self.__count = 0

        # Lift the information to the [$Grow-Data] context.
        self.__lift_to_search_context__()

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
        OPAQUE    = 1
        SEARCHRQ = 1 << 2   # [$]

        data      = self.data
        for pos in range(rawlength):
            pixel = data[pos]
            # Hard coded "Any neighbor" addition policy:
            if not pixel & OPAQUE and ((pos > first_row       and data[pos - rows] & OPAQUE ) or     # Has a opaque neighbor at north.
                                       (pos < last_row        and data[pos + rows] & OPAQUE ) or     # ::     ::      ::     at south.
                                       (pos % rows            and data[pos - 1] & OPAQUE )    or     # ::     ::      ::     at west.
                                       (pos % rows < last_col and data[pos + 1] & OPAQUE )    ):     # ::     ::      ::     at east.
                data[pos]    |= SEARCHRQ
                search[count] = pos
                count        += 1
        # Count update.
        self.__count = count
        self.__context_update__()
        # For support next and current neighbor, we have to travel under the selected search and lift their context manually.
    def __context_update__( self ):
        # Takes a search, and see which elements are opaques. If they're opaques, then
        # It will annotate those that can be searched. (While those wich we want to add aren't in the search yet)

        states      = self.data
        search      = self.__searchView
        newsearch   = self.__nextView
        environment = self.__environment
        count       = self.__count
        newcount    = 0

        rows      = self.width
        first_row = rows
        last_row  = self.size - rows
        last_col  = rows - 1

        # Current State / Enviroment variables
        # Let's use again the state as all relevant thing.
        WEST     = 1 << 7   # [W]
        NORTH    = 1 << 6   # [N]
        SOUTH    = 1 << 5   # [S]
        EAST     = 1 << 4   # [E]
        NOTDIR   = 0x0F

        NOTNORTH = 0xFF & ~NORTH
        NOTSOUTH = 0xFF & ~SOUTH
        NOTWEST  = 0xFF & ~WEST
        NOTEAST  = 0xFF & ~EAST

        # For states:
        MODIFIED = 1 << 3
        NOTMODIF = 0xFF & ~ MODIFIED
        SEARCHRQ = 1 << 2   # [$]
        OPAQUE   = 1        # [O]
        IGNORE   = SEARCHRQ | OPAQUE

        # TODO: Try invert loop order and see what happens.
        # Lookup for states
        for record in range(count):
            pos   = search[record]
            state = states[pos]
            # Better approach:
            if state & OPAQUE:
                # We have to grow add to the neighbors into the search.
                if pos > first_row and not states[pos - rows] & IGNORE:
                    # ADD NORTH
                    states[pos - rows] |= SEARCHRQ
                    newsearch[newcount] = pos - rows
                    newcount           += 1

                if pos < last_row and not states[pos + rows] & IGNORE:
                    # ADD SOUTH
                    states[pos + rows] |= SEARCHRQ
                    newsearch[newcount] = pos + rows
                    newcount           += 1

                if pos % rows and not states[pos - 1] & IGNORE:
                    # ADD WEST
                    states[pos - 1]    |= SEARCHRQ
                    newsearch[newcount] = pos - 1
                    newcount           += 1

                if pos % rows < last_col and not states[pos + 1] & IGNORE:
                    # ADD EAST
                    states[pos + 1] |= SEARCHRQ
                    newsearch[newcount] = pos + 1
                    newcount           += 1
            else:
                # It's transparent.
                # So, we remove the previous direction data:
                state &= NOTDIR

                # and update neighbor/environment info:
                if pos > first_row and states[pos - rows] & OPAQUE:
                    state |= NORTH
                if pos < last_row and states[pos + rows] & OPAQUE:
                    state |= SOUTH
                if pos % rows and states[pos - 1] & OPAQUE:
                    state |= WEST
                if pos % rows < last_col and states[pos + 1] & OPAQUE:
                    state |= EAST

                states[pos]         = state
                newsearch[newcount] = pos
                newcount           += 1

        self.__count = newcount 
        self.__searchView , self.__nextView = self.__nextView , self.__searchView

    def getSearch(self):
        return (self.__searchView , self.__count)

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
    # TODO: It's biased to left-up corner
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
        # Current State / Enviroment variables
        WEST     = 1 << 7   # [W]
        NORTH    = 1 << 6   # [N]
        SOUTH    = 1 << 5   # [S]
        EAST     = 1 << 4   # [E]

        # Next Environment variables
        XWEST    = 1 << 3   # [*W]
        XNORTH   = 1 << 2   # [*N]
        XSOUTH   = 1 << 1   # [*S]
        XEAST    = 1 << 0   # [*E]

        # For states:
        EXPLORED = 1 << 3   # [!]
        SEARCHRQ = 1 << 2   # [$]
        OPAQUE   = 1        # [O]

        # TODO: Optimize!
        # It has to mark where it can grow, then It can grow.

        # So, Here we mark to where each pixel inside the search can grow.

        # For now, it only updates the states.
        for record in range(count):
            pos     = search[record]
            #env     = environment[pos]
            if grow_policy( states[pos] ):
                states[pos] |= OPAQUE
        self.__context_update__()

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
