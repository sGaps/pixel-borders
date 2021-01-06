try:
    from krita      import Selection , Krita , ManagedColor
except:
    print( "[Arguments] Krita Not available" )

# Debug module
from sys            import stderr
# Critical built-in modules
from struct         import pack , unpack
from collections    import deque
# Critical custom modules
from .AlphaGrow     import Grow
from .AlphaScrapper import Scrapper
from .FrameHandler  import FrameHandler
from .Service       import Service , Client

METHODS = { "force"             : Grow.force_grow             ,
            "any-neighbor"      : Grow.any_neighbor_grow      ,
            "corners"           : Grow.corners_grow           ,
            "not-corners"       : Grow.not_corners_grow       ,
            "strict-horizontal" : Grow.strict_horizontal_grow ,
            "strict-vertical"   : Grow.strict_vertical_grow   }

COLOR_TYPES = { "FG" , "BG" , "CS" }
# Keys used in the data structure passed by the GUI
KEYS = {  "q-recipedsc" , # Quick Recipe Descriptor.
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

class KisDepth( object ):
    """
        Manages the krita depth
    """
    def __init__( self , dname ):
        """ dname(str): depth name """
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
            self.valid = True
        else:
            self.valid = False
    def __bool__( self ):
        return self.valid

    def componentSize( self ):
        return self.cast_sz

    def getMin( self ):
        return 0
    def getMax( self ):
        return self.max_val

    def componentCast( self , opaqueValue , managed_components ):
        """ 
            managed_components([float]): where each element is normalized between 0 and 1
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
        return pack(self.cast_str , self.cast_fn(self.max_val))

    def castMin( self ):
        return pack(self.cast_str , 0)

# BUG: There's something here or in the Borderizer that is making some weird results with "F16"
class KisData( object ):
    """ Parse an raw dict object for the borderizer.
        NOTE: This exists for avoid weird issues with Qt memory management
        Tries to put everything in the python realm! """
    def __init__( self , data = {} ):
        """ Implements parse logic. """
        self.valid = False
        self.err   = ""
        if data:    # DO NOT RAISE EXCEPTIONS IF THERE'S NO DATA TO PARSE.
            self.updateAttributes( data )

    @staticmethod
    def pairToMethod( rawMethodDesc ):
        method = METHODS.get( rawMethodDesc[0] , None )
        if method: return ( method , rawMethodDesc[1] )
        raise AttributeError( f"{method} is not a valid method name." )

    def addResult( self , result ):
        self.result = result

    def updateAttributes( self , data ):
        """ data(dict):"""
        dataset = set( data.keys() )
        if KEYS.difference( dataset ):
            raise AttributeError( "provided keys: {dataset} don't match with the required keys {KEYS}" )
        
        # [ ] Trivial:
        self.name = data["name"]

        # [.] Primitive:
        self.node = data.get( "node" , None )
        self.doc  = data.get( "doc"  , None )
        self.kis  = data.get( "kis"  , None )
        if not ( self.node and self.doc and self.kis ):
            raise AttributeError( f"Couldn't run with incomplete information: node = {self.node}, krita = {self.kis}, document = {self.doc}" )

        # [@] Color:
        self.win  = self.kis.activeWindow()
        self.view = self.win.activeView() if self.win else None
        if not ( self.win and self.view ):
            raise AttributeError( f"Couldn't run with incomplete information: window = {self.win}, view = {self.view}" )

        colorType , components = data["colordsc"]
        if colorType == "FG":
            mcolor = self.view.foregroundColor()
        elif colorType == "BG":
            mcolor = self.view.backgroundColor()
        else:
            mcolor = ManagedColor( self.node.colorModel() , self.node.colorDepth() , self.node.colorProfile() )
            mcolor.setComponents( components )
        # This explicit conversion is totally required because Krita's View objects sometimes don't
        # update the color space of user's color (foreground and background colors)
        mcolor.setColorSpace( self.node.colorModel() , self.node.colorDepth() , self.node.colorProfile() )

        # [B] Color to Bytes:
        self.depth       = KisDepth( mcolor.colorDepth() )
        self.components  = mcolor.components()

        # _Pixel and component_
        # NOTE: trPixel = nocolor , opPixel = color , trBytes = trBytes , opBytes = opBytes | after = before
        self.trPixel = self.depth.componentCast( self.depth.getMin() , self.components )
        self.opPixel = self.depth.componentCast( self.depth.getMax() , self.components )
        self.trBytes = self.depth.castMin()
        self.opBytes = self.depth.castMax()
        # _Int Values_
        self.maxVal    = self.depth.getMax()
        self.minVal    = self.depth.getMin()

        # TODO: Fix the threshold error
        useOpaqueAsTransparency , threshold_percent = data["trdesc"]
        self.transparency = self.maxVal if useOpaqueAsTransparency else self.minVal
        # BUG: Threshold has a big error interval.
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
        
        # [P] Parent Node:
        self.parent   = self.node.parentNode()

        # [&] Abstract Objects:
        self.scrapper     = Scrapper()
        self.frameHandler = FrameHandler( self.doc , self.kis , debug = False )

        # [/] Timeline:
        # BUG: Timeline is not correctly defined
        if data["try-animate"]:
            primTimeline = data["animation"]
            self.timeline            = self.frameHandler.get_animation_range( self.node , *primTimeline ) # [start, finish]
            if self.timeline:
                self.start , self.finish = self.timeline.start , self.timeline.stop - 1
            else:
                self.start , self.finish = 0 , 1
        else:
            self.timeline = None

        # UPDATE: Service and Client built for manage concurrent requests.
        self.service = Service()
        self.client  = Client( self.service )

        # [OK] All done:
        self.valid = True

    def __bool__( self ):
        return self.valid

