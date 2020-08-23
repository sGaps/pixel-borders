# Module:      core.FrameHandler.py | [ Language Python ]
# Created by: ( Gaps | sGaps | ArtGaps )
# -----------------------------------------------------
""" Defines a FrameHandler object to manage few special operations like
    import animations and export krita nodes as files. """
from   collections import deque
from   sys         import stderr
import krita
import os
DEFAULT_OUTPUT_DIR = ".output"
# TODO: OPTIMIZE!
class FrameHandler( object ):
    # TODO: add an attribute called: force_write to verify when the file must be written at any cost.
    def __init__( self , doc , krita_instance , subfolder = DEFAULT_OUTPUT_DIR , xRes = None , yRes = None , info = None ):
        self.kis    = krita_instance
        self.doc    = doc
        self.bounds = doc.bounds()
        self.sub    = subfolder.strip()
        self.docdirpath    = f"{ os.path.dirname(doc.fileName()) }"
        self.exportdirpath = f"{ self.docdirpath }/{ subfolder }"
        self.exported      = []
        self.exportReady   = False

        if xRes is None: self.xRes = doc.xRes()
        else:            self.xRes = xRes
        if yRes is None: self.yRes = doc.yRes()
        else:            self.yRes = yRes

        if info is None: self.info = FrameHandler.__default_info__()
        else:            self.info = info

    @staticmethod
    def __default_info__():
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
        """ Sets the export InfoObject. """
        self.info = info

    def setRes( self, xRes , yRes ):
        """ Sets the export resolution. """
        self.xRes = xRes
        self.yRes = yRes

    def __exhaustive_is_animated__( self , node ):
        """ Returns true if there's an animated node in the tree node-hierarchy described by 'node'. """
        queue = deque([node])
        while queue:
            n = queue.pop()
            if n.animated(): return True
            # insert the child nodes into the search queue:
            for c in n.childNodes():
                queue.append(c)
        return False

    def __get_first_frame_index__( self , node , start , finish ):
        """ Returns the first frame of the node in the timeline.
            If it isn't animated, returns None. """
        if not node.animated(): return None

        t         = start
        while not node.hasKeyframeAtTime(t) and t <= finish:
            t += 1
        return t

    def __get_last_frame_index__( self , node , start , finish ):
        """ Returns the first frame of the node in the timeline.
            If it isn't animated, returns None. """
        if not node.animated(): return None

        t         = finish
        while not node.hasKeyframeAtTime(t) and t >= start:
            t -= 1
        return t

    # TODO: Optimize
    def __get_frame_limits_( self , node , start , length ):
        """ returns the first and last frame-indexes inside the range of start-index
            with a given length of the search.
            returns None if there isn't any frame or animation."""
        if not node.animated():
            return None

        frames = [ f for f in range(start,start+length) if node.hasKeyframeAtTime(f) ]
        if frames:
            return [frames[0],frames[-1]]
        else:
            return None

    # Returns all the animated subnodes and the minimum first frame-index
    def __exhaustive_take_animated_nodes__( self , node , start , length ):
        """ Returns the list of animated nodes and the index
            of the first key frame on the timeline.
            
            method (...) => (animated_nodes,first_frame) """
        animated_nodes = []
        queue          = deque([node])
        #first_frame    = None
        anim_limits    = []
        while queue:
            n       = queue.pop()
            limits  = self.__get_frame_limits_(n,start,length+1)  # Note
            #current = self.__get_first_frame_index__(n,start,finish)
            if limits is not None:
                # Add the node to the result:
                animated_nodes.append(n)
                # Update the first frame:
                if anim_limits:
                    anim_limits[0] = min(anim_limits[0],limits[0])
                    anim_limits[1] = max(anim_limits[1],limits[1])
                else:
                    anim_limits = limits

            # Search in the child nodes:
            for c in n.childNodes():
                queue.append(c)
        if anim_limits:
            return ( animated_nodes , range(*anim_limits) )
        else:
            return ( animated_nodes , None )

    def get_animation_of( self , node , start , finish ):
        return __exhaustive_take_animated_nodes__( node , start , finish+1 )

    def get_animation_range( self , node , start , finish ):
        """ Returns a range for the animation if there's animation. Else
            returns None. """
        return self.__exhaustive_take_animated_nodes__( node , start , finish+1 )[1]

    def get_animated_subnodes( self , node , start , finish ):
        """ Returns all the nodes in the node-hierarchy for the animation if there's animation. Else
            returns []. """
        return self.__exhaustive_take_animated_nodes__( node , start , finish+1 )[0]

    def get_exported_files( self ):
        return self.exported

    def build_directory( self ):
        while not self.exportReady:
            try:
                os.makedirs( self.exportdirpath )
            except FileNotFoundError:
                print( f"[FrameHandler]: couldn't create: {self.exportdirpath} trying again " , file = stderr )
                self.exportdirpath = os.path.dirname( self.doc.fileName() ) + "/" + DEFAULT_OUTPUT_DIR
                print( f"                with a new name {self.exportdirpath}." , file = stderr )
                self.exportReady = False
            except FileExistsError:
                self.exportReady = True
            else:
                self.exportReady = True

    def exportFrame( self , filename , node ):
        """ Export the node data of the current time to a file and records the file path into )
            the object. 
            if info object wasn't defined. then filename must have the suffix of png files."""
        if self.exportReady:
            filepath = f"{self.exportdirpath}/{filename}"
            print( f"[FrameHandler]: Trying to export > {filepath}" , file = stderr )
        else:
            print( f"[FrameHandler]: {self.exportdirpath} doesn't exist. Export failed" , file = stderr )
            return False

        batchmodeK = self.kis.batchmode()
        batchmodeD = self.doc.batchmode()
        self.kis.setBatchmode( True )
        self.doc.setBatchmode( True )
        try:
            # Node must return True if everything is right. But it doesn't so...
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
        """ Import files from export directory path saved in the object.
            NOTE: export directory must exist, else no action are performed. """
        searchpath = self.exportdirpath
        if files:
            frames = files
        else:
            framenames = os.listdir( searchpath )
            frames     = [ f"{searchpath}/{f}" for f in framenames ]

        batchmode  = self.kis.batchmode()
        self.kis.doc.setBatchmode( True )
        try:
            if not self.doc.importAnimation( frames , startframe , step ):
                raise ImportError( f"Unable to export animation frames from {self.exportdirpath}" )
            done = True
        except ImportError as error:
            print( error , file = stderr )
            done = False
        self.kis.setBatchmode( batchmode )
        return done

if __name__ == "__main__":
    import krita
    kis = krita.Krita.instance()
    doc  = kis.activeDocument()
    node = doc.activeNode()
    f = FrameHandler(node,doc,72,72,"test_gui/subfolder")
    print( f.__exhaustive_take_animated_nodes__(node,0,20) )
    print( f.exportFrame( "abcd.png"  , node ) )

    infoTest = False
    if infoTest:
        info = krita.InfoObject()
        info.setProperties({
            "alpha":True ,
            "compression":1 , #None
            "forceSRGB":False ,
            "indexed":False ,
            "interlaced":False ,
            "saveSRGBProfile":False ,
            "transparencyFillColor":[]
                    })
        print( info.properties() )
