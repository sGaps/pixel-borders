# Module:      core.Arguments.py | [ Language Python ]
# Author:   Gaps | sGaps | ArtGaps
# LICENSE:  GPLv3 (available in ./LICENSE.txt)
# -------------------------------------------------------
"""
    Defines several objects to parse Real World (krita) data.

    [:] Defined in this module
    --------------------------
    KisColor    :: class
        Parse Krita's color data.

    KisData    :: class
        Parse a raw dict object retrieved from Krita. A valid KisData
        object can be passed safely into a Border Object to get a new
        border layer.

    METHODS     :: dict
        Holds all grow methods currently available with their names.

    COLOR_TYPES :: set
        Holds the supported color types by a Border object.

    KEYS        :: dict
        Holds the required data to run a Borderizer object.
            "debug":        Boolean value. Enables standard profiler prints on stderr.
            "q-recipedsc":  Quick Method descriptor. List with the form [(str,int)]
                            which will be converted to a grow recipe when 'is-quick'
                            is enabled.
            "c-recipedsc":  Custom Method descriptor. Similar to 'q-recipedsc'.
                            used when 'is-quick' isn't enabled.
            "is-quick":     Boolean value. Enabled or disabled when user check or
                            uncheck the Quick Border option.
            "colordsc":     Color descriptor. Iterable with the form [str, [int]]
                            The first element must be in COLOR_TYPES.
                                example: ["FG" , _   ] node's Foreground used.
                                         ["BG" , _   ] node's Background used.
                                         ["CS" , comp]  Custom Managed Color Used. <<used for debugging purposes>>
                                where comp are color components (normalized)
            "trdesc":       Transparency descriptor. Iterable like: [boolean,float]
                                [ use_transparency_as_opque , threshold ]
            "node":         Krita's source node.
            "kis" :         Krita's instance.
            "doc":          Krita's document.
            "animation":    Inclusive Animation range. Iterable with the form [start,end]
                               where start, end are Ints
            "name":         New border's name.

    DEPTHS          :: dict
        Holds relevant information about the color Depth, like cast string and
        max values.

    [*] Author
     |- Gaps : sGaps : ArtGaps
"""
# Debug module
from sys            import stderr
from struct         import pack , unpack
from collections    import deque

try:
    from krita      import Krita , ManagedColor
except:
    print( "[Arguments] Krita Not available" , file = stderr )

# Critical custom modules
from .AlphaGrow     import Grow
from .AlphaScrapper import Scrapper
from .AnimationHandler import AnimationHandler
from .Service       import Service , Client

METHODS = { "force"             : Grow.force_grow             ,
            "any-neighbor"      : Grow.any_neighbor_grow      ,
            "corners"           : Grow.corners_grow           ,
            "not-corners"       : Grow.not_corners_grow       ,
            "strict-horizontal" : Grow.strict_horizontal_grow ,
            "strict-vertical"   : Grow.strict_vertical_grow   }

COLOR_TYPES = { "FG" , "BG" , "CS" }
# Keys used in the data structure passed by the GUI
KEYS = {  "debug"       , # Enable profiler?
          "q-recipedsc" , # Quick Recipe Descriptor.
          "c-recipedsc" , # Custom Recipe Descriptor.
          "is-quick"    , # If true, Use q-recipedsc instead of c-recipedsc.
          "colordsc"    , # Color Descriptor.
          "trdesc"      , # Transparency Descriptor.
          "node"        , # Current Node.
          "doc"         , # Current Document.
          "kis"         , # Current Krita instance.
          "animation"   , # Animation bounds.
          "try-animate" , # Make animated border when it's possible.
          "name"        , # Border name.
          }

# Support for krita color depths. Key -> ( Read_Write_Pattern , Max_Value )
DEPTHS = { "U8"  : ("B" , 2**8  - 1 ) ,
           "U16" : ("H" , 2**16 - 1 ) ,
           "F16" : ("e" , 1.0       ) ,
           "F32" : ("f" , 1.0       ) }

class KisColor( object ):
    """
        Manages the krita's depths in the Python's realm
    """
    def __init__( self , managed_color ):
        """ ARGUMENTS:
                dname(str): depth name
        """
        mcolor = managed_color
        dname  = mcolor.colorDepth()
        dstats = DEPTHS.get( dname , None )
        if dstats:
            # Get the number
            self.cast_sz = int( dname[1:] )
            # Get the cast string and the maximum value that can holds the numeric type
            self.cast_str , self.max_val = dstats
            # Get the cast function
            if dname[0] == "U":
                self.cast_fn = int
            else:
                self.cast_fn = float

            # Copy the color data
            self.colorDepth   = dname
            self.colorModel   = mcolor.colorModel()
            self.colorProfile = mcolor.colorProfile()

            self.valid = True
        else:
            self.valid = False
    def __bool__( self ):
        return self.valid

    def componentSize( self ):
        """ RETURNS
                int. the number of bytes used to each color component. """
        return self.cast_sz

    def getMin( self ):
        """ RETURNS
             int. The minimum value of the color component. """
        return 0
    def getMax( self ):
        return self.max_val

    def componentCast( self , opaqueValue , managed_components ):
        """ ARGUMENTS
                managed_components([float]): where each element is
                                             normalized between 0 and 1
            RETURNS
                A bytes-like object. A color raw component.
        """
        color      = bytearray()
        components = managed_components
        ncomps     = len(components)
        dmax       = self.getMax()
        for i in range(ncomps - 1):
            color += pack( self.cast_str , self.cast_fn(components[i] * dmax) )

        opaqueBytes = pack( self.cast_str , opaqueValue )
        return color + opaqueBytes

    def castMax( self ):
        """ RETURNS
                A bytes-like object. The maximum raw color component. """
        return pack(self.cast_str , self.cast_fn(self.max_val))

    def castMin( self ):
        """ RETURNS
                A bytes-like object. The minimum raw color component. """
        return pack(self.cast_str , 0)

# TODO: Add a new attribute to set the number of workers in each step.
class KisData( object ):
    """ Parse an raw dict object for the borderizer.
        NOTE: This exists to avoid weird issues with Qt's memory management (its GC)
              This tries to put everything in the python's realm! """
    def __init__( self , data = {} ):
        """ Implements parse logic. """
        self.valid = False
        self.err   = ""
        if data:    # Do not raise exceptions if there's no data to parse.
            self.updateAttributes( data )

    @staticmethod
    def pairToMethod( rawMethodDesc ):
        """ ARGUMENTS
                rawMethodDesc((str,int)): Basic recipe descriptor.
            RETURNS
                (Grow.method,int). An smart recipe descriptor. """
        method = METHODS.get( rawMethodDesc[0] , None )
        if method: return ( method , rawMethodDesc[1] )
        raise AttributeError( f"{method} is not a valid method name." )

    def addResult( self , result ):
        """ ARGUMENTS
                result(object): element to save.
            Holds a reference of an external result that can be used to avoid
            Qt's garbage collector wild decisions. """
        self.result = result

    def show( self , file = stderr ):
        """ ARGUMENTS
                file: Where the current information will be displayed.
            Debug method that prints information about the current KisData. """
        report = lambda *msg: print( "[Kis Data]: " , *msg , file = file )
        if not self.valid:
            report( "Invalid Object" )
            return

        report( f"Name:             {self.name}" )
        report( f"Document:         {self.doc }" )
        report( f"Krita:            {self.kis }" )
        report( f"Window:           {self.win }" )
        report( f"View:             {self.view}" )
        report( f"components:       {self.components}" )
        report( f"Kis Color:        {self.kiscolor}" )
        report( f"transp. Pixel:    {self.trPixel}" )
        report( f"opaque. Pixel:    {self.opPixel}" )
        report( f"bytes. Transp.:   {self.trBytes}" )
        report( f"bytes. Opaque.:   {self.opBytes}" )
        report( f"max Value:        {self.maxVal }" )
        report( f"min Value:        {self.minVal }" )
        report( f"transparency:     {self.transparency}" )
        report( f"threshold:        {self.threshold}" )
        report( f"recipe:           {self.recipe}" )
        report( f"thickness:        {self.thickness}" )
        report( f"batchmode Krita:  {self.batchK}" )
        report( f"batchmode Doc.:   {self.batchD}" )
        report( f"channels:         {self.channels}" )
        report( f"nchans:           {self.nchans}" )
        report( f"Current Node:     {self.node  }" )
        report( f"Parent Node:      {self.parent}" )
        report( f"Take Bounds From: {self.constraint}" )
        report( f"Scrapper:         {self.scrapper}" )
        report( f"Start Time:       {self.start}" )
        report( f"Finish Time:      {self.finish}" )
        report( f"Timeline Range:   {self.timeline}" )
        report( f"Service:          {self.service}" )

    def updateAttributes( self , data , test_color = None ):
        """ ARGUMENTS
                data(dict): Raw Krita's data.
                test_color(krita.ManagedColor): overrides window/view's current colors [optional, only for debugging]
            EXCEPTIONS
                AttributeError. If data has wrong values.
            Parse krita's data to make it safe to use."""
        dataset = set( data.keys() )
        diff    = KEYS.difference( dataset )
        if diff:
            raise AttributeError( f"The keys: {diff} weren't provided. " +
                                  f"Unable to run with: {dataset}. Required keys: {KEYS}" )

        # [ ] Trivial:
        self.name  = data["name"]
        self.debug = data["debug"]

        # [.] Primitive:
        self.node = data.get( "node" , None )
        self.doc  = data.get( "doc"  , None )
        self.kis  = data.get( "kis"  , None )
        if not ( self.node and self.doc and self.kis ):
            raise AttributeError( f"Couldn't run with incomplete information: " +
                                  f"node = {self.node}, krita = {self.kis}, document = {self.doc}" )

        # [@] Color:
        self.win  = self.kis.activeWindow()
        self.view = self.win.activeView() if self.win else None
        if not ( self.win and self.view ):
            error = AttributeError( f"Couldn't run with incomplete information: " +
                                    f"window = {self.win}, view = {self.view}" )
        else:
            error = None

        colorType , components = data["colordsc"]
        if colorType == "FG":
            if error: raise error
            mcolor = self.view.foregroundColor()
        elif colorType == "BG":
            if error: raise error
            mcolor = self.view.backgroundColor()
        else:
            mcolor = ManagedColor( self.node.colorModel() , self.node.colorDepth() , self.node.colorProfile() )
            mcolor.setComponents( components )
        # This explicit conversion is totally required because Krita's View objects don't
        # update the color space of user's color (foreground and background colors)
        mcolor.setColorSpace( self.node.colorModel() , self.node.colorDepth() , self.node.colorProfile() )

        # [B] Color to Bytes:
        self.kiscolor    = KisColor( mcolor )
        self.components  = mcolor.components()
        kiscolor         = self.kiscolor

        # _Pixel and component_
        # NOTE: trPixel = nocolor , opPixel = color , trBytes = trBytes , opBytes = opBytes | after = before
        self.trPixel = kiscolor.componentCast( kiscolor.getMin() , self.components )
        self.opPixel = kiscolor.componentCast( kiscolor.getMax() , self.components )
        self.trBytes = kiscolor.castMin()
        self.opBytes = kiscolor.castMax()
        # _Int Values_
        self.maxVal    = kiscolor.getMax()
        self.minVal    = kiscolor.getMin()

        # TODO: Fix the threshold error
        useOpaqueAsTransparency , threshold_percent = data["trdesc"]
        self.transparency = self.maxVal if useOpaqueAsTransparency else self.minVal
        self.threshold = int( self.maxVal * (threshold_percent/100) ) if self.node.colorDepth() in {"U8","U16"} else self.maxVal * (threshold_percent/100)

        # [*] Method (it can raise an exception inside the list comprension)
        primRecipe      = data["q-recipedsc"] if data["is-quick"] else data["c-recipedsc"]
        self.recipe     = [ KisData.pairToMethod(desc) for desc in primRecipe ]
        self.thickness  = sum( map(lambda tupl: tupl[1] , self.recipe) )

        # [<] Rollback state:
        self.batchK , self.batchD = self.kis.batchmode() , self.kis.batchmode()

        # [C] Node's channels:
        self.channels = self.node.channels()
        self.nchans   = len( self.channels )
        self.chsize   = len( self.opBytes ) # Alternative: use len( self.trBytes )

        # [P] Parent Node:
        self.parent   = self.node.parentNode()

        # [&] Abstract Objects:
        self.scrapper     = Scrapper()
        self.animHandler = AnimationHandler( self.doc , debug = False )

        # [/] Timeline:
        if data["try-animate"]:
            primTimeline  = data["animation"]
            self.timeline = AnimationHandler.extract_animation_range_of( self.node , *primTimeline ) # [start, finish]
            if self.timeline:
                self.start , self.finish = self.timeline.start , self.timeline.stop - 1
            else:
                self.start , self.finish = 0 , 1
        else:
            self.start , self.finish = 0 , 1
            self.timeline = None

        # [S] Service and Client has been built to serialze concurrent requests.
        self.service = Service()

        # NOTE: Filter masks aren't supported because these doesn't have useful bounds for this plugin.
        # UPDATE: Bounds cannot be retrieved directly from the source node or
        #         they will ignore the efects of transformation/filter masks!
        # --------------------------------------------------------------------
        # :-: Krita's Layer
        #   :-: transform mask top            <<<<  This has the most recent bound information of the Krita's Layer
        #   :-: transform mask middle               so, we must use them in the "Reading" Step.
        #   :-: transform mask bottom
        TOP             = -1
        transform_masks = [ mask for mask
                            in self.node.childNodes()
                            if mask.visible() and mask.type() == "transformmask" ]
        self.constraint = self.node
        if transform_masks:
            self.constraint = transform_masks[TOP] # Take it from the top.

        # [OK] All done:
        self.valid = True

    def __bool__( self ):
        return self.valid

