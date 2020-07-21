from krita         import Selection , Krita

# TODO: DELETE THIS BLOCK [BEGIN]
if __name__ == "__main__":
    import sys
    import os
    PACKAGE_PARENT = '..'
    SCRIPT_DIR = os.path.dirname(os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__))))
    sys.path.append(os.path.normpath(os.path.join(SCRIPT_DIR, PACKAGE_PARENT)))
# TODO: DELETE THIS BLOCK [END]

# TODO: Move this to front:
from core.AlphaGrow     import Grow
from core.AlphaScrapper import Scrapper

class Borderizer( object ):
    def __init__( self , node , doc , view ):
        self.node = node
        self.doc  = doc
        self.view = view
        # Initializer
        s         = Scrapper()
        self.data = s.extract_alpha( node , doc )
        self.g    = Grow( node , width , True )

        # Convenience:
        b           = doc.bounds()
        self.bounds = b

        # Non Python-Pure:
        self.Opaque = Selection()
        self.Opaque.setPixelData( self.data , b.x() , b.y() , b.width() , b.height() )

    def __abstract_grow__( self , thickness , grow_method ):
        for i in range(thickness):
            grow_method()

    def classic( self , thickness ):
        self.__abstract_grow__( thickness , self.g.classic_grow )

    def corners( self , thickness ):
        self.__abstract_grow__( thickness , self.g.corners_grow )

    def classic_then_corners( self , thickness , splitIndex ):
        """ apply classic into [0..splitIndex-1] then
            apply corners into [splitIndex..length] """
        if splitIndex < 0 or thickness < 0:
            return
        self.classic(splitIndex)
        self.corners(thickness-splitIndex+1)
        
    def corners_then_classic( self , thickness , splitIndex ):
        """ apply corners into [0..splitIndex-1] then
            apply classic into [splitIndex..length] """
        if splitIndex < 0 or thickness < 0:
            return
        self.corners(splitIndex)
        self.classic(thickness-splitIndex+1)

    # TODO: Add a max depth of recursion global parameter
    def nodeOrChildrenAreAnimated( self , node ):
        if node.animated():
            return True
        for n in node.childNodes():
            if self.nodeOrChildrenAreAnimated( self , node ):
                return True
        return False

    def bordersIntoFrames( self , name , start , finish , color ,thickness , splitIndex = -1 , mode = "classic" ):
        if   mode == "classic":
            border_method = self.classic()
            method_args   = [thickness]
        elif mode == "corners":
            border_method = self.corners()
            method_args   = [thickness]
        elif mode == "classic_then_corners":
            border_method = self.classic_then_corners()
            method_args   = [thickness,splitIndex]
        elif mode == "corners_then_classic":
            border_method = self.corners_then_classic()
            method_args   = [thickness,splitIndex]

        if not self.nodeOrChildrenAreAnimated( self.node ):
            finish = start + 1
        # TODO: Manage color before things in fill method and after fill method.
        flatten_method = self.kis.action( "convert_group_to_animated" )
        fill_method    = self.kis.action( "fill_selection_foreground_color")
        self.__abstract_borders_into_frames__( name , self.node , self.doc , self.view  , start , finish ,
                                               color , flatten_method , fill_method , border_method , method_args )


    # TODO: MANAGE the case of animated/non-animated node in a concrete method.
    # NOTE: If node isn't animated or if it hasn't animated subnodes, then: finish = start+1
    # NOTE: method_args = [thickness,splitIndex] | [thickness]
    # TODO: Change the fill method <fill_foreground = self.kis.action( "fill_selection_foreground_color")> by other clearer.
    def __abstract_borders_into_frames__( self , name , node , doc , view , start , finish , color ,
                                                 flatten_method , fill_method , border_method , *method_args ):
        timeline = range( start , finish + 1 )
        before   = range( 0 , start )

        # TODO: Manage
        # Backup data:
        prevTime  = doc.current_time()
        prevSelec = doc.selection()
        prevColor = view.foregroundColor()

        # Empty Frames:
        frames = self.doc.createGroupLayer( name )
        node.parentNode().addChildNode( frames , self.node )

        # Fill the first steps with empty "frames"
        current  = None
        previous = None
        for t in before:
            previous = current
            current  = self.doc.createNode( str(t) , "paintlayer" )
            frames.addChildNode( current , previous )

        # Puts the color:
        view.setForeGroundColor( color )
        # Generate the actual borders:
        current  = None
        previous = None
        for t in timeline:
            # Update frame projection (Using Krita-Actions):
            doc.setCurrentTime(t)
            doc.refreshProjection()
            doc.waitForDone()           # TODO: Search if this is totally required

            # Build a new node (frame for frame group)
            previous = current
            current  = doc.createNode( str(t) , "paintlayer" )
            doc.setActiveNode( current )

            # Add the node to the group:
            frames.addChildNode( current , previous )
            
            # Selects the border of the origin node:
            border = border_method( method_args ) # Need to use Python * and ** for support various kinds of parameters
            doc.setSelection( border )

            # Fill with the fg-color, then waits until complete that action:
            fill_method()
            doc.refreshProjection()
            doc.waitForDone()           # TODO: Search if this is totally required
        
        # Group Layer flat (Using Krita-Actions):
        doc.setActiveNode( frames )
        flatten_method()
        doc.refreshProjection()
        doc.waitForDone()           # TODO: Search if this is totally required

        # Closing actions:
        # TODO: Change view.setForeGroundColor( with fill_method )
        view.setForeGroundColor( prevColor )
        doc.setActiveNode( node )
        doc.setCurrentTime( prevTime )
        doc.setSelection( prevSelec )
        doc.refreshProjection()

    # Lookup:
    def getBorderSelection( self ):
        border = Selection()
        b      = self.bounds
        border.setPixelData( self.data , b.x() , b.y() , b.width() , b.height() )
        border.subtract( self.Opaque )
        return border

# ---------------------------
# TODO: DELETE THIS
if __name__ == "__main__":
    kis = Krita.instance()
    d = kis.activeDocument()
    n = d.activeNode()
    for child in n.childNodes():
        print( child )
# ----------------------------
