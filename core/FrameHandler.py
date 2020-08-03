from collections import deque
import os
import krita

kis                = krita.Krita.instance()
DEFAULT_OUTPUT_DIR = ".output"
# ALWAYS EXPORT AS PNG, so default info is always for png and its updates to the node contents.
class FrameHandler( object ):
    def __init__( self , node , doc , krita_instance , subfolder = DEFAULT_OUTPUT_DIR , xRes = None , yRes = None ,  , info = None ):
        self.kis    = krita_instance
        self.doc    = doc
        self.bounds = doc.bounds()
        self.sub    = subfolder.strip()
        self.node   = node
        self.docdirpath    = f"{ os.path.dirname(doc.filename()) }"
        self.exportdirpath = f"{ self.docdirpath }/{ subfolder }"
        self.exported      = []
        self.exportReady   = False

        if xRes is None: self.xRes = doc.xRes()
        else:            self.xRes = xRes
        if yRes is None: self.yRes = doc.yRes()
        else:            self.yRes = yRes
        if info is None: self.info = self.__default_info__( node )
        else:            self.info = info

    def __default_info__( self , node ):
        info = krita.InfoObject()
        info.setProperties({
            "alpha"                 : True  ,   # Always must be true
            "compression"           : 1     ,   # No compression
            "forceSRGB"             : False ,   # Ensures few things
            "indexed"               : False ,   # Ensures few things
            "interlaced"            : False ,   #
            "saveSRGBProfile"       : False ,   #
            "transparencyFillColor" : []        # No color for this because we save the alpha channel
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

    # Returns all the animated subnodes and the minimum first frame-index
    def __exhaustive_take_animated_nodes__( self , node , start , finish ):
        """ Returns the list of animated nodes and the index
            of the first key frame on the timeline.
            
            method (...) => (animated_nodes,first_frame) """
        animated_nodes = []
        queue          = deque([node])
        first_frame    = None
        while queue:
            n       = queue.pop()
            current = self.__get_first_frame_index__(n,start,finish)
            if current is not None:
                # Add the node to the result:
                animated_nodes.append(n)
                # Update the first frame:
                if first_frame is None: first_frame = current
                else:                   first_frame = min(first_frame,current)

            # Search in the child nodes:
            for c in n.childNodes():
                queue.append(c)
        return (animated_nodes,first_frame)

    def get_animation_range( self , start , finish ):
        """ Returns a range for the animation if there's animation. Else
            returns None. """
        _ , first = self.__exhaustive_take_animated_nodes__( self.node , start , finish )
        if first is None:   return None
        else:               return range( first ,
                                          self.__get_last_frame_index__(self.node , first+1 , finish+1) )

    def get_animated_subnodes( self , start , finish ):
        """ Returns all the nodes in the node-hierarchy for the animation if there's animation. Else
            returns None. """
        nodes , *_ = self.__exhaustive_take_animated_nodes__( self.node , start , finish )
        return nodes

    def get_exported_files( self ):
        return self.exported

    def __build__directory__( self ):
        while not self.exportReady:
            try:
                os.mkdir( self.exportdirpath )
            except FileNotFoundError:
                self.exportdirpath = os.path.dirname( self.doc.fileName() ) + "/" + DEFAULT_OUTPUT_DIR
                self.exportReady = False
            except FileExistsError:
                self.exportReady = True
            else:
                self.exportReady = True

    def exportFrame( self , filename , node ):
        """ Export the node data of the current time to a file and records the file path into
            the object. """
        self.__build__directory__()

        batchmode  = self.kis.batchmode()
        self.kis.setBatchmode( True )
        try:
            filepath = f"{self.exportdirpath}/{filename}"
            result = node.save( filepath , self.xRes , self.yRes , self.info , self.bounds )
            # Record the path of the all files exported.
            self.exported.append(filepath)
        except:
            result = None
        self.kis.setBatchmode( batchmode )
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
            # TODO: Print into stderr
            print( error.args )
            done = False
        self.kis.setBatchmode( batchmode )
        return done

if __name__ == "__main__":
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
