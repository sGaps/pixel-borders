from PyQt5.QtWidgets import QApplication , QVBoxLayout , QLabel

# TODO: Clean this sequence
from importlib import reload
try:
    # Krita has some problems with module paths (why? idk)
    import pixel_borders.gui.SmartMenu  as SM
    import pixel_borders.gui.MenuPage   as MP
    import pixel_borders.gui.NamePage   as NP
    import pixel_borders.gui.TypePage   as YP
    import pixel_borders.gui.ColorPage  as KP
    import pixel_borders.gui.QuickPage  as QP
    import pixel_borders.gui.CustomPage as CP
    import pixel_borders.gui.WaitPage   as WP
    import pixel_borders.gui.TdscPage   as TP
    import pixel_borders.gui.AnimPage   as AP
    outsideKRITA = False
except:
    import gui.SmartMenu  as SM
    import gui.MenuPage   as MP
    import gui.NamePage   as NP
    import gui.TypePage   as YP
    import gui.ColorPage  as KP
    import gui.QuickPage  as QP
    import gui.CustomPage as CP
    import gui.WaitPage   as WP
    import gui.TdscPage   as TP
    import gui.AnimPage   as AP
    outsideKRITA = True

# TODO: Delete later
# NOTE: I'm able to use this with
reload( SM )
reload( MP )
reload( NP )
reload( YP )
reload( KP )
reload( QP )
reload( CP )
reload( WP )
reload( TP )
reload( AP )

Menu       = SM.Menu
MenuPage   = MP.MenuPage
NamePage   = NP.NamePage
TypePage   = YP.TypePage
ColorPage  = KP.ColorPage
QuickPage  = QP.QuickPage
CustomPage = CP.CustomPage
WaitPage   = WP.WaitPage
TdscPage   = TP.TdscPage
AnimPage   = AP.AnimPage

if outsideKRITA:
    main = QApplication([])

class GUI( object ):
    def __init__( self , title = "Pixel Borders" , parent = None ):
        menu = Menu()

        namep   = NamePage  ()
        typep   = TypePage  ( namep   )
        colorp  = ColorPage ( typep   )
        quickp  = QuickPage ( colorp  )
        customp = CustomPage( colorp  )
        tdscp   = TdscPage  ( customp )
        animp   = AnimPage  ( tdscp   )
        waitp   = WaitPage  ()

        # Next Connections:
        namep.next   = typep      # (1 -> 2)
        typep.next   = colorp     # (2 -> 3)
        colorp.next , colorp.altn = quickp , customp    # (3 -> 4.a | 4.b)
        quickp.next  = waitp
        customp.next = tdscp
        tdscp.next   = animp
        animp.next   = waitp

        # Krita-Dependent Code:
        animp.connect_with_krita()

        # Connections between Pages:
        typep.type_changed.connect( colorp.serve_negated_alternative_request )
        typep.type_changed.connect( animp.setOverride )

        # Connections between Pages and Menu:
        namep.cancel.released.connect  ( menu.reject          )
        namep.info.released.connect    ( menu.displayInfo     )
        waitp.cancel.released.connect  ( menu.tryRollBack     )
        waitp.info.released.connect    ( menu.displayInfo     )
        namep.previous.released.connect( menu.usePreviousData )

        menu.addPage( namep   , "name"   )
        menu.addPage( typep   , "type"   )
        menu.addPage( colorp  , "color"  )
        menu.addPage( quickp  , "quick"  )
        menu.addPage( customp , "custom" )
        menu.addPage( tdscp   , "transp" )
        menu.addPage( animp   , "anim"   )
        menu.addPage( waitp   , "wait"   )

        menu.setupDefaultConnections()
        menu.sendRequestWhenCurrentPageIs( "wait" )

        self.menu = menu

    def run( self ):
        self.menu.show()

        if outsideKRITA:
            main.exec_()

    def connectWithBorderizer( self , borderizer ):
        self.menu.connectWithBorderizer( borderizer )

# NOTE: I had some issues trying to run the kritarunner of Krita 4.4.x. It seems that it requires
#       a function with type (f :: a -> () ). So, I use for test this safely...
#       >>>     $ kritarunner -s SetupGUI -f test
def test( _ ):
    gui = GUI( "Pixel Borders - Test" )
    gui.run()

if __name__ == "__main__":
    gui = GUI( "Pixel Borders - Test" )
    gui.run()
