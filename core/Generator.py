from .Arguments import KisData
from .KisStatus import KisStatus , ALPHA
from .AlphaGrow import Grow
from queue      import SimpleQueue


class Generator( object ):
    """ Make borders to each layer """ 
    def __init__( self , kis_arguments  = KisData()          ,
                         inQueue        = SimpleQueue()      ,
                         outQueue       = SimpleQueue()      ,
                         status         = KisStatus()        ,
                         report         = (lambda msg: None) ,
                         error          = (lambda msg: None) ,
                         stepDone       = (lambda:     None) ): # 'Atomic' Increment
        super().__init__()
        self.args   = kis_arguments
        # In/Out
        self.raw  = inQueue
        self.done = outQueue
        self.status = status
        
        # Messages and more:
        self.report = report
        self.error  = error
        self.stepDone = stepDone

    @staticmethod
    def runRecipe( grow , recipe ):
        """
            ARGUMENTS
                grow(AlphaGrow.Grow):               Grow object.
                recipe([AlphaGrow.Grow.method()):   describes how to make border grow
            RETURNS
                AlphaGrow.Grow
            Apply the grow recipe to the grow object. """
        [
            [ task(grow) for i in range(steps) ]    # Apply a grow-task as many steps required.
            for task , steps in recipe              # Take a task and how many steps will be applied from the recipe.
        ]
        return grow

    # IO (queue<ALPHA>) -> IO (queue<ALPHA>)
    def run( self ):
        """
            Make borders using the source node's alpha data.
        """
        raw    = self.raw
        done   = self.done
        status = self.status
        recipe = self.args.recipe

        # I/O Reports ------------
        report   = self.report
        error    = self.error
        stepDone = self.stepDone

        runRecipe  = Generator.runRecipe
        grow       = Grow.singleton()

        while True:
            if not status.keepRunning():
                report( "core.Generate: Canceled by user." )
                break
            try:
                # Exit when it's empty:
                falpha = raw.get_nowait()
            except:
                break
            
            alpha  = falpha.alpha
            time   = falpha.time
            bounds = falpha.bounds

            # [B] Bounds dependent ------------------
            width  = bounds.width()
            length = width * bounds.height()
            # ---------------------------------------

            # [G] Generate Border -------------------
            grow.setData( alpha , width , length )
            runRecipe( grow , recipe )
            # ---------------------------------------
            
            done.put(
                ALPHA(grow.difference_with( alpha ),
                      time,
                      bounds)
                    )

            # [*] PROGRESS BAR:
            stepDone()
        # All done.

