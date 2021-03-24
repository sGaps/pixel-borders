# Module:   core.AlphaGrow.py | [ Language Python ]
# Author:   Gaps | sGaps | ArtGaps
# LICENSE:  GPLv3 (available in ./LICENSE.txt)
# -------------------------------------------------
"""
    [:] Defined in this module
    --------------------------
        Grow    :: class
            Automata used to make grow the alpha data just like
            how krita.Selection's grow method works.

        TYPES   :: dict
            Holds relevant information about the size of the indexes, like
            the byte sizes and cast strings that can be used on memoryview
            objects.

        $Grow-State :: Abstraction
            bit field (int) made for model the grow data from a Grow object.

    [*] Author
     |- Gaps : sGaps : ArtGaps
"""
TYPES = { 1 : "B" ,
          2 : "H" ,
          4 : "I" ,
          8 : "L" }

class Grow( object ):
    """
        An Grow object is an automata. It takes the raw alpha data from a Node
        (processed by an Scrapper) and apply grows operations just like Krita's
        Selection Layers.

        Each Grow's element is used as a 8-bit field, which is referred as
        [$Grow-State]. These are managed with bitswise operations to keep
        them in a small size. An opaque pixel is represented with an
        element with an Opaque bit on.

        The bits of an element [$Grow-State] are:
            bit 7:  Can grow to West    [W]         | "Environment
            bit 6:  Can grow to North   [N]         | Values" or
            bit 5:  Can grow to South   [S]         | "Neighborhood
            bit 4:  Can grow to East    [E]         | Data".
            bit 3:  --- ---- -- -----   [ ]
            bit 2:  Search Request      [$]             | Basic
            bit 1:  --- ---- -- -----   [ ]             | Search
            bit 0:  Is Opaque           [O]             | Criteria.

        An horizontal representation may be:
            bit   >     76543210
            field >     WNSE $ O

        A way recipe to look up these bits is use bitwise operations with
        these values:
            WEST  = 1 << 7  = 0x80
            NORTH = 1 << 6  = 0x40
            SOUTH = 1 << 5  = 0x20
            EAST  = 1 << 4  = 0x10

        Use unlift_data to get a clean bytearray that can be used outside
        these objects.

        Relevant internal structures:
            __modified      :: memoryview( BYTE ) => holds the modified pixels after a __run_automata__ step.
            __preserved     :: memoryview( BYTE ) => holds the preserved pixels after a __run_automata__ step.
            __searchView    :: memoryview( BYTE ) => holds the indexes that will be used in a __run_automata__ step.

        * Preserved elements are these considered as transparent after a __run_automata__ step.
        * Modified elements are these considered as opaques after a __run_automata__ step.
    """
    def __init__( self , data , width , size , amount_of_items_on_search = None ):
        """
            ARGUMENTS
                data(bytearray):                alpha data.
                width(int):                     width of the canvas.
                size(int):                      size or raw length of the alpha data.
                amount_of_items_on_search(int): # of elements that will be cached in the search.
                                                If it's none, then The amount will take a value automatically.

            Save shared information for futher method applications.
            """

        self.data         = None    # User canvas data.
        self.size         = None    # Number of pixels.
        self.width        = None    # Width of each column.

        # Objects used for update $Grow-State context.
        self.__searchView = None    # [Integer]: Holds the elements to search in each __run_automata__ iteration.
        self.__modified   = None    # [Integer]: Holds the index of each modified element of the search.
        self.__preserved  = None    # [Ingeger]: Holds the index of each not-modified element of the search.
        self.__indexSize  = None    # Int
        self.__count      = None    # Int: Number of elements in the search
        self.__cmodif     = None    # Int: Number of elements modified.
        self.__cpresv     = None    # Int: Number of elements not-modified (preserved)
        self.__staticsize = 0

        self.setData( data , width , size , force_amount_of_items_on_search = amount_of_items_on_search )

    @classmethod
    def singleton( cls , amount_of_items_on_search = None ):
        """ RETURNS
                Trivial Grow object.
        """
        return cls( bytearray() , 0 , 0 , amount_of_items_on_search )

    @classmethod
    def __get_required_bytes_for__( cls , size ):
        """ RETURNS
                Number of bytes used by a search index.
        """
        limit = 1 << 8
        for k in TYPES:
            if size < limit: return k
            else:            limit <<= 8
        raise TypeError( f"Size uses too many bytes. Available bytes sizes: {set(TYPES.keys())}" )

    def setData( self , data , width , size , force_amount_of_items_on_search = None ):
        """
            ARGUMENTS
                data(bytearray):                        alpha data.
                width(int):                             width of the canvas.
                size(int):                              size of the alpha data.
                force_amount_of_items_on_search(int):   # of elements that will be cached in the search.
                                                        (Useful when the previous data is as big as the current one).
            Smart constructor/Setter of a Grow object. """

        # Builds new data:
        self.data = bytearray( 0x01 if b else 0x00 for b in data )
        self.width    = width
        self.size     = size

        self.__indexSize   = Grow.__get_required_bytes_for__( size )
        required_size      = size * self.__indexSize

        # Try to avoid new memoryview allocations each time this method is called:
        if force_amount_of_items_on_search:
            # Recalculate values:
            self.__indexSize = Grow.__get_required_bytes_for__( force_amount_of_items_on_search )
            required_size    = force_amount_of_items_on_search * self.__indexSize

            if force_amount_of_items_on_search != self.__staticsize or not self.__searchView:
                # Cast each bytearray into a static integer type, based in the size required for
                # represent the maximum index-value of the canvas.
                self.__searchView = memoryview( bytearray(required_size) ).cast( TYPES[self.__indexSize] )
                self.__modified   = memoryview( bytearray(required_size) ).cast( TYPES[self.__indexSize] )
                self.__preserved  = memoryview( bytearray(required_size) ).cast( TYPES[self.__indexSize] )
            self.__staticsize = force_amount_of_items_on_search

        elif not self.__staticsize and (not self.__searchView or len( self.__searchView ) != size):
            # Cast each bytearray into a static integer type, based in the size required for
            # represent the maximum index-value of the canvas.
            self.__searchView = memoryview( bytearray(required_size) ).cast( TYPES[self.__indexSize] )
            self.__modified   = memoryview( bytearray(required_size) ).cast( TYPES[self.__indexSize] )
            self.__preserved  = memoryview( bytearray(required_size) ).cast( TYPES[self.__indexSize] )

        # Always resets the indexes.
        self.__count  = 0
        self.__cmodif = 0
        self.__cpresv = 0

        # Lift the information to the [$Grow-State] context.
        self.__lift_to_search_context__()

    def __lift_to_search_context__( self ):
        """
            Convert the stored raw data into a [$Grow-State] sequence. The Grow
            instance will be valid after call this method.
        """
        # Search is not defined yet. We only have "modified elements" for now.
        states    = self.data
        modified  = self.__modified
        count     = 0

        # Position variables:
        rawlength = self.size
        rows      = self.width
        first_row = rows - 1
        last_row  = rawlength - rows
        last_col  = rows - 1

        # [$Grow-State] Access constants:
        SEARCHRQ  = 1 << 2  # [$]
        OPAQUE    = 1       # [O]
        IGNORE    = OPAQUE

        start     = 0
        while True:
            pos = states.find( OPAQUE , start )
            if pos < 0:
                break
            else:
                start = pos + 1

            if ( (  pos > first_row       and not states[pos - rows] & IGNORE ) or
                 (  pos < last_row        and not states[pos + rows] & IGNORE ) or
                 (  pos % rows            and not states[pos - 1]    & IGNORE ) or
                 (  pos % rows < last_col and not states[pos + 1]    & IGNORE ) ):
                # Doesn't require to add a search request:
                modified[count] = pos
                count          += 1
        # Count update:
        self.__cmodif = count
        self.__context_update__()

    def __context_update__( self ):
        """
            Updates the [$Grow-State] Neighborhood data and its Basic
            Search Criteria.
        """
        # Takes a search 'log', and see which elements are opaques. If they're opaques, then
        # It will mark those that can be searched. (And adds those which aren't in the search yet).

        # Indices & data arrays:
        states      = self.data
        search      = self.__searchView
        modified    = self.__modified
        preserved   = self.__preserved

        # Relevant indexes:
        newcount    = 0
        modif_count = self.__cmodif
        presv_count = self.__cpresv

        # Relevant bounds:
        rows      = self.width
        first_row = rows - 1
        last_row  = self.size - rows
        last_col  = rows - 1

        # [$Grow-State] Access constants:
        WEST     = 1 << 7   # [W]
        NORTH    = 1 << 6   # [N]
        SOUTH    = 1 << 5   # [S]
        EAST     = 1 << 4   # [E]
        NOTDIR   = 0x0F     # -[W,N,S,E]

        SEARCHRQ = 1 << 2   # [$]
        OPAQUE   = 1        # [O]
        IGNORE   = SEARCHRQ | OPAQUE    # [$ + O]

        # Opaque traversal:
        for record in range(modif_count):
            pos   = modified[record]
            state = states[pos]

            # Search the transparent elements that aren't in the search yet.
            if pos > first_row and not states[pos - rows] & IGNORE:
                # ADD NORTH
                states[pos - rows]    |= SEARCHRQ
                preserved[presv_count] = pos - rows
                presv_count           += 1

            if pos < last_row and not states[pos + rows] & IGNORE:
                # ADD SOUTH
                states[pos + rows]    |= SEARCHRQ
                preserved[presv_count] = pos + rows
                presv_count           += 1

            if pos % rows and not states[pos - 1] & IGNORE:
                # ADD WEST
                states[pos - 1]       |= SEARCHRQ
                preserved[presv_count] = pos - 1
                presv_count           += 1

            if pos % rows < last_col and not states[pos + 1] & IGNORE:
                # ADD EAST
                states[pos + 1]       |= SEARCHRQ
                preserved[presv_count] = pos + 1
                presv_count           += 1

        # Transparent traversal:
        for record in range(presv_count):
            pos   = preserved[record]
            state = states[pos]

            # Clean the previous Direction data:
            state &= NOTDIR

            # Update neighborhood/environment data:
            if pos > first_row and states[pos - rows] & OPAQUE:
                state |= NORTH  # Has a North Opaque
            if pos < last_row and states[pos + rows] & OPAQUE:
                state |= SOUTH
            if pos % rows and states[pos - 1] & OPAQUE:
                state |= WEST
            if pos % rows < last_col and states[pos + 1] & OPAQUE:
                state |= EAST

            states[pos]      = state
            search[newcount] = pos
            newcount        += 1

        self.__count = newcount

    def getSearch(self):
        """
            RETURNS
                the search array and the elements on search.
        """
        return (self.__searchView , self.__count)

    def __any_neighbor_policy__( self , environment ):
        """
            ARGUMENTS
                environment($Grow-State):   represents the
                                            enviroment/neighborhood of the pixel.
            RETURNS
                int used as bool.
            returns true if the environment has at least one neighbor.
            [W] | [N] | [S] | [E] = 1
        """
        return environment & 0xF0

    def __is_corner_policy__( self , environment ):
        """
            ARGUMENTS
                environment($Grow-State):   represents the
                                            enviroment/neighborhood of the pixel.
            RETURNS
                int used as bool.
                                                                     TRUE IF:
            Grows only if the enviroment can be considered as       |'' , ''| ,
            a corner. It is Iff has only one vertical and one       |__ , __| , ...
            horizontal neighbor.
            WEST  = 1 << 7  = 0x80
            NORTH = 1 << 6  = 0x40
            SOUTH = 1 << 5  = 0x20
            EAST  = 1 << 4  = 0x10
        """
        h  = 1 if environment & 0x80 else 0
        h += 1 if environment & 0x10 else 0
        if h != 1: return 0x00
        v  = 1 if environment & 0x40 else 0
        v += 1 if environment & 0x20 else 0
        return 0x01 if h == v else 0x00

    def __not_corner_policy__( self , environment ):
        """
            ARGUMENTS
                environment($Grow-State):   represents the
                                            enviroment/neighborhood of the pixel.
            RETURNS
                int used as bool.
            negate version of __is_corner_policy__
        """
        return not self.__is_corner_policy__( environment )

    def __always_grow_policy__( self , _ ):
        """
            ARGUMENTS
                environment($Grow-State):   represents the
                                            enviroment/neighborhood of the pixel.
            RETURNS
                int used as bool.
            No matter what happens, always grow.
        """
        return 0x01

    def __strict_horizontal_policy__( self , environment ):
        """
            ARGUMENTS
                environment($Grow-State):   represents the
                                            enviroment/neighborhood of the pixel.
            RETURNS
                int used as bool.
            Grows only if the block has any horizontal neighbor
            WEST  = 1 << 7  = 0x80
            NORTH = 1 << 6  = 0x40
            SOUTH = 1 << 5  = 0x20
            EAST  = 1 << 4  = 0x10
            """
        return ( 0x00 if environment & (0x40 | 0x20)
                      else environment & (0x80 | 0x10) )

    def __strict_vertical_policy__( self , environment ):
        """
            ARGUMENTS
                environment($Grow-State):   variable that represents the enviroment of the pixel.
            RETURNS
                int used as bool.
            Grows only if the block has any vertical neighbor
            WEST  = 1 << 7  = 0x80
            NORTH = 1 << 6  = 0x40
            SOUTH = 1 << 5  = 0x20
            EAST  = 1 << 4  = 0x10
            """
        return ( 0x00 if environment & (0x80 | 0x10)
                      else environment & (0x40 | 0x20) )

    def __run_automata__( self , grow_policy ):
        """
            ARGUMENTS
                grow_policy( function($Grow-State)
                            -> int): Takes an $Grow-State element and return a
                                     value else than 0 when the pixel must be
                                     opaque.

            This modifies the internal structure of a Grow instance. Updates the
            alpha data based on the grow_policy function. """
        # Indices & data arrays:
        newcount    = 0
        count       = self.__count
        search      = self.__searchView

        modified    = self.__modified
        preserved   = self.__preserved
        modif_count = 0
        presv_count = 0

        states      = self.data # States = Data + context

        # Relevant bounds:
        rows      = self.width
        first_row = rows - 1
        last_row  = self.size - rows
        last_col  = rows - 1

        # [$Grow-State] Access constant:
        OPAQUE   = 1        # [O]

        # For now, it only updates the states.
        for record in range(count):
            pos     = search[record]
            if grow_policy( states[pos] ):
                # Modify state
                states[pos]            |= OPAQUE
                # Add to modified element list
                modified[ modif_count ] = pos
                modif_count            += 1
            else:
                # Add to preserved element list
                preserved[ presv_count ] = pos
                presv_count += 1

        # Update counters:
        self.__cmodif = modif_count
        self.__cpresv = presv_count
        self.__context_update__()

    def force_grow( self ):
        """ Grows always. """
        self.__run_automata__( self.__always_grow_policy__ )

    def any_neighbor_grow( self ):
        """" A pixel is opaque if it has an opaque neighbor. """
        self.__run_automata__( self.__any_neighbor_policy__ )

    def corners_grow( self ):
        """ A pixel is opaque if it's also a corner. """
        self.__run_automata__( self.__is_corner_policy__ )

    def not_corners_grow( self ):
        """ A pixel is opaque when it's not in a corner. """
        self.__run_automata__( self.__not_corner_policy__ )

    def strict_horizontal_grow( self ):
        """ A pixel is opaque if it doesn't have an opaque vertical neighbor. """
        self.__run_automata__( self.__strict_horizontal_policy__ )

    def strict_vertical_grow( self ):
        """ A pixel is opaque if it doesn't have an opaque horizontal neighbor. """
        self.__run_automata__( self.__strict_vertical_policy__ )

    def grow_with_custom_policy( self , grow_policy ):
        """ ARGUMENTS
                grow_policy( $Grow-State -> int or bool ): Uses a function to
                                                           decide when a pixel
                                                           must be opaque.
            A pixel is opaque if grow_policy say it. """
        self.__run_automata__( grow_policy )

    def unlift_data( self ):
        """ RETURNS
                bytearray
            Returns a new bytearray without the [$Grow-State] bit field context.
            The returned data can be used outside this object. """
        return bytearray( 0xFF if p & 0x01 else 0x00 for p in self.data )

    def difference_with( self , external ):
        """
            ARGUMENTS
                external(bytearray): external to apply difference with it.
            RETURNS
                bytearray
            SEE ALSO
                unlift_data
            Similar to unlift_data, but applies difference operation while
            between the internal and external alpha data.
        """
        # Unlift the Grow context and apply difference:
        d = self.data
        return bytearray( 0xFF & ~external[i] if d[i] & 0x01 else 0x00 for i in range(self.size) )

    def xor_with( self , external ):
        """
            ARGUMENTS
                external(bytearray): external to apply xor with it.
            RETURNS
                bytearray
            SEE ALSO
                unlift_data
            Similar to unlift_data, but applies xor before return the new
            bytearray object.
            """
        # Unlift the Grow context and apply XOR
        d = self.data
        return bytearray( external[i] ^ 0xFF if d[i] & 0x01 else external[i] ^ 0x00 for i in range(self.size) )
