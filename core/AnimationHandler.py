# Module:   core.AnimationHandler.py | [ Language Python ]
# Author:   Gaps | sGaps | ArtGaps
# LICENSE:  GPLv3 (available in ./LICENSE.txt)
# -------------------------------------------------------
"""
    Defines some classes to handle Krita's files and animations.

    [:] Defined in this module
    --------------------------
    RESOLUTION :: namedtuple( Int , Int )
        class used to represent the resolution of an image.

    ANIMATED_NODES :: namedtuple( [krita.Node] , range )
        class used to represent the relevant animation nodes data.

    error :: func( str ) -> IO ()
        prints error messages on stderr

    AnimationHandler :: class
        It's used to verify if a node has key-frames and to export and
        import files on Krita.

    [*] Author
     |- Gaps : sGaps : ArtGaps
"""
from collections import deque, namedtuple
from sys         import stderr
from tempfile    import mkdtemp

import os
try:
    from krita import InfoObject
except:
    InfoObject = None
    print( "[Animation Handler]: Krita not available" )


class RESOLUTION(
    namedtuple(
        typename    = 'RESOLUTION',
        field_names = ['xRes','yRes']
              )
           ): pass

class ANIMATED_NODES(
    namedtuple(
        typename    = 'ANIMATED_NODES',
        field_names = ['nodes','anim_range']
              )
           ): pass

DEFAULT_PREFIX = "pxlb_"
def error( msg ):
    print( msg , file = stderr )

class AnimationHandler( object ):
    """
        Utility object used to verify if a node has keyframes,
        to export frames of a krita's node and to import animation
        keyframes using the last exported data.
    """
    def __init__( self , document , exportdirpath = "" , resolution = None , infoObj = None , debug = False ):
        self.doc       = document
        self.bounds    = document.bounds()
        # I/O Management:
        self.exportdir   = exportdirpath
        self.exportReady = len(exportdirpath) > 0
        self.exported    = []

        # Debug:
        self.debug = (lambda msg : print( msg , file = stderr )) if debug else (lambda msg: None)

        # Resolution: Use Document's resolution if None is provided
        self.resolution = resolution or RESOLUTION(document.xRes(), document.yRes())
        self.info       = infoObj    or AnimationHandler.basicInfoObject()

    def get_export_dir( self ):
        """
            RETURNS
                the current export directory """
        return self.exportdir

    def get_exported_file_basenames( self ):
        """
            RETURNS
                the current files exported by this object """
        return self.exported

    @staticmethod
    def basicInfoObject():
        """
            RETURNS
                krita.InfoObject. A simple InfoObject. """
        if InfoObject:
            info = InfoObject()
            info.setProperties({
                "alpha"                 : True  ,   # Always must be true
                "compression"           : 1     ,   # No compression
                "forceSRGB"             : False ,   # Ensures few things
                "indexed"               : False ,   # Ensures few things
                "interlaced"            : False ,   #
                "saveSRGBProfile"       : False ,   #
                "transparencyFillcolor" : [255,255,255]
                        })
        else:
            info = None
        return info

    @staticmethod
    def animation_range_of( node , start , length ):
        """
            ARGUMENTS
                node(krita.Node): target node.
                start(int):       first frame of the animation range.
                length(int):      number of frames in the animation range.
            RETURNS
                list if node has keyframes. [start,end], both extremes are inclusives.
                None if it doesn't.
            """
        if not node.animated():
            return None

        anim_range = [ t for t in range(start,start+length+1) if node.hasKeyframeAtTime(t) ]
        if anim_range:
            return [anim_range[0],anim_range[-1]]
        else:
            return None

    @staticmethod
    def extract_animation_range_of_subtree( root_node , start , length ):
        """
            ARGUMENTS
                root_node(krita.Node):  root node of the node's hierarchy.
                start(int):             first frame of the animation range.
                length(int):            number of frames in the animation range.
            RETURNS
                ANIMATED_NODES(nodes=[krita.Node],range=[int])
                    where nodes is the list of animated nodes,
                          anim_range is a inclusive timeline range where one of these nodes has a keyframe.

                    NOTE: nodes is empty and range is None when there isn't any node with keyframes in
                          the original range(start,length+1)
        """
        animated_nodes = []
        queue          = deque([root_node])
        anim_limits    = []

        # Search:
        while queue:
            node    = queue.pop()
            limits  = AnimationHandler.animation_range_of(node,start,length)

            if limits is not None:
                # Add the node to the result:
                animated_nodes.append(node)
                # Update the first frame:
                if anim_limits:
                    anim_limits[0] = min(anim_limits[0],limits[0])
                    anim_limits[1] = max(anim_limits[1],limits[1])
                else:
                    anim_limits = limits

            # Add children to search:
            for c in node.childNodes():
                queue.append(c)
        if anim_limits:
            return ANIMATED_NODES( nodes      = animated_nodes,
                                   anim_range = range(anim_limits[0],anim_limits[1]+1))
        else:
            return ANIMATED_NODES( nodes      = animated_nodes ,
                                   anim_range = None )

    @staticmethod
    def extract_animation_of( node, start , finish ):
        """
            RETURNS
                the animation data retrieved from node
        """
        length = finish - start + 1
        return AnimationHandler.extract_animation_range_of_subtree( node , start , length )

    @staticmethod
    def extract_animation_range_of( node , start , finish ):
        """
            RETURNS
                the animation range retrieved from node
        """
        data = AnimationHandler.extract_animation_of( node , start , finish )
        return data.anim_range

    @staticmethod
    def extract_animated_nodes_of( node , start , finish ):
        """
            RETURNS
                the animated nodes retrieved from node
        """
        data = AnimationHandler.extract_animation_of( node , start , finish )
        return data.nodes

    def build_directory( self ):
        """
            Create the export directory in the system's temporal directory.
        """
        if self.exportReady: return True

        self.exportdir   = mkdtemp( prefix = DEFAULT_PREFIX )
        self.exportReady = len( self.exportdir) > 0
        if not self.exportReady:
            error( "[Animation Handler]: Unable to make temporary directory." )
        return self.exportReady

    def clean_up_all( self ):
        """
            Deletes the internal directory from the system's temporal directory.
        """
        frame_names = [ f"{self.exportdir}/{frame}" for frame in self.exported ]
        try:
            for f in frame_names:
                os.remove( f )
            try:
                os.rmdir( self.exportdir )
            except:
                error( f"[Animation Handler] Unable to remove [ {self.exportdir} ]" )
                return False

            return True
        except:
            error( f"[Animation Handler] Unable to remove exported files." )
            return False

    def export( self , file_basename , node ):
        """
            Save the current node's data in a file called file_basename. That file will
            be in the current export directory (if exists).

            NOTE: You must enable batchmode for Krita.instance() and current Document before use this.
                  or it will display a popup every time this runs.
        """
        result = False
        if self.exportReady:
            filepath = f"{self.exportdir}/{file_basename}"
        else:
            self.debug( f"[Animation Handler]: Export directory doesn't exist < {self.exportdir} >" )
            return result

        try:
            # Node must return True if everything is right. But it doesn't, so...
            node.save( filepath , *self.resolution , self.info , self.bounds )
            # I handle this manually...
            result = os.path.exists( filepath )

            # Record only the name. The final user must concatenate the name with 
        except:
            result = False

        if result: self.exported.append(file_basename)
        return result

    def get_exported_file_basenames( self ):
        """ RETURNS
                the exported file base names."""
        return self.exported

    @staticmethod
    def import_frames( document , startframe , files = [] ):
        """
            General way to import frames from krita.
        """
        if not files:
            return False

        done = True
        if not document.importAnimation( files , startframe , 1 ): # (which files, first frame, step between frames)
            error( "[Animation Handler]: Unable to import animation frames" )
            done = False

        return done

    def import_by_basename( self , startframe , file_basenames = [] ):
        """
            Import frames using the current export directory
        """
        if not self.exportReady:
            error( "[Animation Handler]: Cannot import without any previous export directory" )
            return False

        searchpath  = self.exportdir
        frame_names = file_basenames.copy()
        frame_names.sort()
        frame_names = [ f"{searchpath}/{frame}" for frame in frame_names ]
        return AnimationHandler.import_frames( self.doc , startframe , frame_names )

