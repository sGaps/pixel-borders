# Module:      core.FrameHandler.py | [ Language Python ]
# Created by: ( Gaps | sGaps | ArtGaps )
# -----------------------------------------------------
# TODO: DELETE THIS, IT'S DEPRECATED
"""
    Defines a FrameHandler object to manage few special operations like
    import animations and export krita nodes as files.

    [:] Defined in this module
    --------------------------
    FrameHandler        :: class
        Manages I/O operations. It's used when a node has keyframes
        in a Krita.Animation.

    DEFAULT_OUTPUT_DIR :: str
        name of the default directory which is used by a FrameHandler object
        to export frames from an Krita's animation.

    [*] Author
     |- Gaps : sGaps : ArtGaps
"""
from collections    import deque
from sys            import stderr
from tempfile       import mkdtemp
import os
try:
    import krita
except:
    print( "[Frame Handler]: Krita not available" )

#DEFAULT_OUTPUT_DIR = ".output"
DEFAULT_PREFIX = "pxlb_"
def error( msg ):
    print( msg , file = stderr )

class FrameHandler( object ):
    """
        Utility object to export and import frames/images from and to krita.
    """
    def __init__( self , doc , krita_instance , exportdirpath = "" , xRes = None , yRes = None , info = None , debug = False ):
        """
            ARGUMENTS
                doc(krita.Document):            Current Document.
                krita_instance(krita.Krita):    Current Krita instance.
                subfolder(str):                 Subfolder used to import and export krita-frames.
                xRes(float):                    x Resolution.
                yRes(float):                    y Resolution.
                info(krita.InfoObject):         Information used to export frames. (export configuration).
                debug(bool):                    enables/disables print operations in the stderr buffer.
        """
        self.kis    = krita_instance
        self.doc    = doc
        self.bounds = doc.bounds()
        self.exportdirpath = exportdirpath
        self.exported      = []
        self.exportReady   = len(exportdirpath) > 0
        self.debug = (lambda msg : print( msg , file = stderr )) if debug else (lambda msg: None)
        if not debug:
            self.debug = lambda msg : ()
        else:
            self.debug = lambda msg : print( msg , file = stderr )

        if xRes is None: self.xRes = doc.xRes()
        else:            self.xRes = xRes
        if yRes is None: self.yRes = doc.yRes()
        else:            self.yRes = yRes

        if info is None: self.info = FrameHandler.__default_info__()
        else:            self.info = info

    @staticmethod
    def __default_info__():
        """
            RETURNS
                krita.InfoObject. A trivial InfoObject. """
        info = krita.InfoObject()
        info.setProperties({
            "alpha"                 : True  ,   # Always must be true
            "compression"           : 1     ,   # No compression
            "forceSRGB"             : False ,   # Ensures few things
            "indexed"               : False ,   # Ensures few things
            "interlaced"            : False ,   #
            "saveSRGBProfile"       : False ,   #
            "transparencyFillcolor" : [255,255,255]
                    })
        return info

    def setInfo( self , info ):
        """
            ARGUMENTS
                info(krita.InfoObject): object used to describe the export options.
            Sets the export InfoObject. """
        self.info = info

    def setRes( self, xRes , yRes ):
        """
            ARGUMENTS
                xRes(float):                    x Resolution
                yRes(float):                    y Resolution
            Sets the export resolution. """
        self.xRes = xRes
        self.yRes = yRes

    def __exhaustive_is_animated__( self , node ):
        """
            ARGUMENTS
                node(krita.Node):   Current node
            RETURNS
                bool. True if there's an animated node in the tree
                node-hierarchy defined by 'node'.
            """
        queue = deque([node])
        while queue:
            n = queue.pop()
            if n.animated(): return True
            # insert the child nodes into the search queue:
            for c in n.childNodes():
                queue.append(c)
        return False

    def __get_first_frame_index__( self , node , start , finish ):
        """
            ARGUMENTS
                node(krita.Node):   source node.
                start(int):         start time index.
                finish(int):        finish time index.
            RETURNS
                int or None

            Returns the first frame index of the node in the timeline.
            If it isn't animated or it doesn't have keyframes, returns None.
            NOTE: this uses a inclusive range [start,finish]
            """
        if not node.animated(): return None

        t         = start
        while not node.hasKeyframeAtTime(t) and t <= finish:
            t += 1
        return t

    def __get_last_frame_index__( self , node , start , finish ):
        """
            ARGUMENTS
                node(krita.Node):   source node.
                start(int):         start time index.
                finish(int):        finish time index.
            RETURNS
                int or None

            Returns the first frame index of the node in the timeline.
            If it isn't animated, returns None.
            NOTE: this uses a inclusive range [start,finish] """
        if not node.animated(): return None

        t         = finish
        while not node.hasKeyframeAtTime(t) and t >= start:
            t -= 1
        return t

    def __get_frame_limits_( self , node , start , length ):
        """
            ARGUMENTS
                node(krita.Node):   source node.
                start(int):         start time index.
                length(int):        length of the animation range.
            RETURNS
                int or None

            returns the first and last frame-indexes inside the range of start-index
            with a given length of the search.
            returns None if there isn't any frame or animation.
            NOTE: this uses an inclusive range [start, length] """
        if not node.animated():
            return None

        frames = [ f for f in range(start,start+length+1) if node.hasKeyframeAtTime(f) ]
        if frames:
            return [frames[0],frames[-1]]
        else:
            return None

    # Returns all the animated subnodes and the minimum first frame-index
    def __exhaustive_take_animated_nodes__( self , node , start , length ):
        """
            ARGUMENTS
                node(krita.Node):   source node.
                start(int):         start time index.
                length(int):        length of the animation range.
            RETURNS
                ( [ krita.Node] , [int] ) or
                ( []            , None  )
            Returns the list of animated nodes and the inclusive indexes
            of the leftmost and rightmost keyframes in the animation
            range [start,length] """
        animated_nodes = []
        queue          = deque([node])
        anim_limits    = []
        # Search:
        while queue:
            n       = queue.pop()
            limits  = self.__get_frame_limits_(n,start,length)
            if limits is not None:
                # Add the node to the result:
                animated_nodes.append(n)
                # Update the first frame:
                if anim_limits:
                    anim_limits[0] = min(anim_limits[0],limits[0])
                    anim_limits[1] = max(anim_limits[1],limits[1])
                else:
                    anim_limits = limits

            # Add children to search:
            for c in n.childNodes():
                queue.append(c)
        if anim_limits:
            return ( animated_nodes , range(anim_limits[0],anim_limits[1]+1) )
        else:
            return ( animated_nodes , None )

    def get_animation_of( self , node , start , finish ):
        """
            ARGUMENTS
                node(krita.Node):   source node.
                start(int):         start time index.
                finish(int):        finish time index.
            RETURNS
                ( [ krita.Node] , [int] ) or
                ( []            , None  )
            Wrapper function of __exhaustive_take_animated_nodes__

            Returns a list of animated nodes and, the leftmost
            and rightmost keyframe indexes of the inclusive
            range [start,finish]
        """
        length = finish - start + 1
        return __exhaustive_take_animated_nodes__( node , start , length )

    def get_animation_range( self , node , start , finish ):
        """
            ARGUMENTS
                node(krita.Node):   source node.
                start(int):         start time index.
                finish(int):        finish time index.
            RETURNS
                [int] or None
            Returns a inclusive range for the animation if there's animation. Else
            returns None.

            See also: get_animation_of"""
        length = finish - start + 1
        return self.__exhaustive_take_animated_nodes__( node , start , length )[1]

    def get_animated_subnodes( self , node , start , finish ):
        """
            ARGUMENTS
                node(krita.Node):   source node.
                start(int):         start time index.
                finish(int):        finish time index.
            RETURNS
                [krita.Node]
            Returns all the nodes in the node-hierarchy for the animation if there's animation. Else
            returns [].
            See also: get_animation_of"""
        length = finish - start + 1
        return self.__exhaustive_take_animated_nodes__( node , start , length )[0]

    def get_exported_files( self ):
        """
            RETURNS
                [ str ]
            Returns a list of all exported keyframes/files.
            each element is a full path to a file.
        """
        if not self.exportReady:
            error( "[Frame Handler]: WARNING! There isn't any export directory. Call build_directory() first!" )
        return self.exported

    def build_directory( self ):
        """
            IO-ACTION
                make the specified subfolder in the current Document path.
                mkdir dirname( krita.activeDocument().fileName() )/subfolder
            RETURNS
                bool
        """
        self.exportdirpath = mkdtemp( prefix = DEFAULT_PREFIX )
        self.exportReady   = len( self.exportdirpath ) > 0
        if not self.exportReady:
            self.debug( f"[FrameHandler]: Unable to make temporal directory" )
        return self.exportReady

    def removeExportedFiles( self ):
        """
            ARGUMENTS
                removeSubFolder(bool): Used to know when is totally required remove the subfolder.
            IO-ACTION
                remove all exported files, while it's allowed.
            RETURNS
                bool
        """
        try:
            for f in self.exported:
                os.remove( f )
            try:
                os.rmdir( self.exportdirpath )
            except:
                self.debug( f"[FrameHandler] Unable to remove the export directory [ {self.exportdirpath} ]." )
                return False

            return True
        except:
            self.debug( f"[FrameHandler] Unable to remove exported files" )
            return False

    def exportFrame( self , filename , node ):
        """
            ARGUMENTS
                filename(str):      name of the file with image extension (.png, jpeg, ...)
                node(krita.Node):   source node.
            IO-ACTION
                Export the node pixel data as filename
            RETURNS
                bool
            Export the node data of the current time to a file and records the file path into )
            the object.
            if info object wasn't defined. then filename must have the suffix of png files."""
        if self.exportReady:
            filepath = f"{self.exportdirpath}/{filename}"
            self.debug( f"[FrameHandler]: Trying to export > {filepath}" )
        else:
            self.debug( f"[FrameHandler]: {self.exportdirpath} doesn't exist. Export failed" )
            return False

        batchmodeK = self.kis.batchmode()
        batchmodeD = self.doc.batchmode()
        self.kis.setBatchmode( True )
        self.doc.setBatchmode( True )
        try:
            # Node must return True if everything is right. But it doesn't, so...
            node.save( filepath , self.xRes , self.yRes , self.info , self.bounds )
            # I handle this in a different way...
            result = os.path.exists( filepath )

            # Record the path of the all files exported.
            self.exported.append(filepath)
        except:
            result = False
        self.kis.setBatchmode( batchmodeK )
        self.doc.setBatchmode( batchmodeD )
        return result

    def importFrames( self , startframe , files = [] ):
        """
            ARGUMENTS
                startframe(int):    start keyframe index to add the animation.
                files([str]):       which files will be used as animation.
            IO-ACTION
                try import all files
            RETURNS
                bool
            Import files from export directory path saved in the object.
            if files is empty, then this uses the exported files.
            NOTE: export directory must exist, else does nothing. """
        searchpath = self.exportdirpath

        if not files:
            files = self.exported

        if files:
            frames = files
        else:
            framenames = os.listdir( searchpath )
            frames     = [ f"{searchpath}/{f}" for f in framenames ]

        batchmode  = self.kis.batchmode()
        batchmodeD = self.doc.batchmode()
        self.doc.setBatchmode( True )

        try:
            if not self.doc.importAnimation( frames , startframe , 1 ): # files([str]) , firstframe(int) , step(int)
                raise ImportError( f"Unable to export animation frames from {self.exportdirpath}" )
            done = True
        except ImportError as error:
            self.debug( error )
            done = False

        self.doc.setBatchmode( batchmodeD )
        self.kis.setBatchmode( batchmode )
        return done
