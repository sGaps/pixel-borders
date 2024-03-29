# Module:   core.Border.py | [ Language Python ]
# Author:   Gaps | sGaps | ArtGaps
# LICENSE:  GPLv3 (available in ./LICENSE.txt)
# ----------------------------------------------
"""
    Defines the actual core of this plugin.

    [:] Defined in this module
    --------------------------
    Border :: class
        Holds relevant information to make a new border layers.
        Create new threads to performs almost all its tasks.
        + Notify the current progress of the border generation process.
        + Notify errors or events occurred in the process.
        + Performs rollback operations when something goes wrong or when
          user cancel the process.

    [*] Author
     |- Gaps : sGaps : ArtGaps
"""
# Plugin's Realm:
from .Reader    import Reader
from .Generator import Generator
from .Writer    import Writer
from .KisStatus import KisStatus
from .Arguments import KisData
from .Service   import Client
# Python's Realm:
from threading  import Thread , Barrier
from queue      import SimpleQueue

# Debugging/Profiling:
import cProfile

# A beautiful non-Qt object.
class Border( object ):
    ANIMATION_IMPORT_DEFAULT_INDEX = -1
    def __init__( self , kis_arguments  = KisData()          ,
                         status         = KisStatus()        ,
                         setSteps       = (lambda start, end: None),
                         resetSteps     = (lambda: None)     ,
                         report         = (lambda msg: None) ,
                         error          = (lambda msg: None) ,
                         stepName       = (lambda msg: None) ,      # must use: waitp.fstep.setText
                         frameNumber    = (lambda num: None) ,      # must use: waitp.updateFrameNumber or something like that
                         frameIncrement = (lambda:     None) ,      # must use: waitp.incrementFrameNumber
                         frameErase     = (lambda:     None) ,      # must use: waitp.reset
                         stepDone       = (lambda:     None) ,      # 'Atomic' Increment
                         workDone       = (lambda:     None) ,
                         rollbackDone   = (lambda:     None) ):
        """
            New Borderizer engine.
            + Notify the current progress of the border generation process.
            + Notify errors or events occurred in the process.
            + Performs rollback operations when something goes wrong or when
              user cancel the process.
        """
        super().__init__()
        self.args     = kis_arguments
        self.status   = status

        self.setSteps   = setSteps
        self.resetSteps = resetSteps
        # I/O Report:
        self.report      = report
        self.error       = error
        self.stepName    = stepName
        self.frameNumber = frameNumber
        self.frameIncrement = frameIncrement
        self.frameErase     = frameErase
        self.stepDone    = stepDone

        # Finalization/Termination/Clean-up:
        self.workDone     = workDone
        self.rollbackDone = rollbackDone
        self.rollbackList = []
        self.targetsDeleted = False

        self.justStop = False

    def cleanRollbackList( self ):
        """
            RETURNS
                current rollback list
        """
        del self.rollbackList
        self.rollbackList = []

    def getStatus( self ):
        """
            RETURNS
                current process status.
        """
        return self.status

    def rollback( self ):
        """ Undo all operations done by this object and its children """
        steps = self.rollbackList
        steps.reverse()
        [ step() for step in steps ]

        self.status.showStatus( self.error )
        self.resetSteps()
        self.rollbackDone()

    def submitRollbackStep( self , rollback_step ):
        """
            ARGUMENTS
                rollback_step( function() -> None ): single rollback step

            Adds a rollback step to the rollback list.
        """
        self.rollbackList.append( rollback_step )

    def hasToExit( self , status ):
        """
            ARGUMENTS
                status(KisStatus): process status.
            RETURNS
                bool
            Verify if the process has recieved a cancellation signal.
            Apply rollback steps if the process if it has been canceled.

            These signals come from the user or from the process itself (or its children)
        """
        if self.justStop: return True

        if status.fromGUI == KisStatus.STOP:
            self.report( "core.Border: Stopped by user" )
            self.error( "[core.Border] <FROM USER>: process canceled!" )
            self.justStop = True

        if status.fromCore == KisStatus.STOP:
            self.error( "[core.Border] <FROM CORE>: An error occurred. Stopping!" )
            self.justStop = True

        if self.justStop:
            self.rollback()
        return self.justStop

    def targets_deleted( self ):
        """ Verify if the target layers has been deleted. """
        return self.targetsDeleted

    def run( self ):
        """ Performs all actions on normal or debug mode. """
        if not self.args:
            return

        if self.args.debug:
            cProfile.runctx( "self.run_now()" , globals() , locals() )
        else:
            self.run_now()

    def progressUpdate( self ):
        """ Refresh the abstract progress status bar. """
        self.frameIncrement()
        self.stepDone()
 

    def run_now( self , nWorkers = 4 ):
        """ Apply all steps to add borders for your paint/group-layer. """
        # Counted by: value<reason>.
        BASIC_STEPS = 1 + 1 + 1 + 1 # 1<import> + 1<temporal dir. deletion> + 1<move border layer> +1<delete/rename temporal targets layers>
        ITER_STEPS  = 1 + 1 + 1     # 1<Reader> + 1<Generator> + 1<Writer>

        STOP    = KisStatus.STOP
        status  = self.status

        # I/O Reports ------------------
        report       = self.report
        error        = self.error
        stepDone     = self.stepDone
        workDone     = self.workDone
        rollbackDone = self.rollbackDone
        stepName     = self.stepName
        frameNumber  = self.frameNumber
        progress     = self.progressUpdate
        frameErase   = self.frameErase

        setSteps   = self.setSteps
        resetSteps = self.resetSteps

        # From Krita ------------------------------
        args            = self.args
        kis             = args.kis
        doc             = args.doc
        animator        = args.animHandler
        original_time   = doc.currentTime()
        batchK , batchD = args.batchK , args.batchD
        client          = Client( args.service )

        report( "Setup batch mode" )
        kis.setBatchmode( True )
        doc.setBatchmode( True )

        # Calculate how many steps this has to do ----
        # NOTE: #F is the number of frames into node's animation.
        # nsteps = #F<Reader> + #F<Grow> + #F<Write> + 1<import> + 1<delete> + 1<move layer>
        nframes = len(args.timeline) if args.timeline else 1
        nsteps  = ITER_STEPS * nframes + BASIC_STEPS - 1 # We do not count step 0.

        resetSteps()
        setSteps( 0 , nsteps )
        
        # |> ROLLBACK >-----------------------------------------------------
        report( "Adding initial Rollback steps" )
        self.submitRollbackStep( lambda: kis.setBatchmode(batchK) )
        self.submitRollbackStep( lambda: doc.setBatchmode(batchD) )
                
        self.submitRollbackStep( lambda: client.serviceRequest( doc.waitForDone ) )
        self.submitRollbackStep( lambda: client.serviceRequest( doc.refreshProjection ) )
        self.submitRollbackStep( lambda: client.serviceRequest( doc.setCurrentTime , original_time ) )
        # |> ROLLBACK >-----------------------------------------------------

        if not args.timeline:
            # It isn't necessary use several threads in this case.
            nWorkers      = 1

        # Step 1: Fetch the alpha channel data of each frame.
        # -------   <*>TAGS:    ROLLBACK (current time),
        #                       KRITA COMMUNICATION,
        #                       SERIAL
        report( "Fetching alpha data" )
        stepName( "Raw Frames:" )
        frameNumber( 0 )
        raw_alphas = SimpleQueue()
        reader = Reader( args,
                         raw_alphas,
                         status,
                         report,
                         status.internalStopRequest,
                         progress )
        reader.run()

        # Step 2: Apply the grow recipe to each alpha data:
        # -------   <*>TAGS:    NO-ROLLBACK,
        #                       PARALLEL
        report( "Building Generators" )
        stepName( "Alpha Frames:" )
        frameNumber( 0 )
        grow_alphas = SimpleQueue()
        generators  = [ Generator( args,
                               raw_alphas,
                               grow_alphas,
                               status,
                               report,
                               status.internalStopRequest,
                               progress ) for _ in range(nWorkers) ]
        tgenerators = [ Thread( target = generators[i].run , name = f"generator-{i}" )
                        for i in range(nWorkers)        ]
        for tg in tgenerators:
            tg.start()
        report( "Making Borders" )

        for tg in tgenerators:
            tg.join()

        del generators
        del tgenerators

        # Makes a new directory for the animation frames when it's possible.
        report( "Making temporary directory for animation" )
        if not animator.build_directory():
            status.internalStopRequest( "[core.Borderizer]: Cannot create a directory for the animation frames.\n"         +
                                        "                 : try to save the file before apply this plugin or\n"            +
                                        "                 : verify if krita has permissions over the temporary directory." )

        # <| ROLLBACK <------------------------
        if self.hasToExit( status ): return
        # <| ROLLBACK <------------------------

        # Step 3: Makes new target nodes to write on them.
        # -------   <*>TAGS:    ROLLBACK (new targets, files exported),
        #                       PARALLEL
        writeDone   = Barrier( parties = nWorkers )
        refreshDone = Barrier( parties = nWorkers )
        flushDone   = Barrier( parties = nWorkers )
        report( f"Building Targets ({nWorkers} of them)" )
        targets = []
        for i in range(nWorkers):
            targets.append( client.serviceRequest(doc.createNode, f".target-{i}", "paintlayer") )
            client.serviceRequest(targets[i].setColorSpace, args.kiscolor.colorModel, args.kiscolor.colorDepth, args.kiscolor.colorProfile)
            client.serviceRequest(args.parent.addChildNode, targets[i], args.node)
        report( "Exporting Borders" )
        stepName( "Frames:" )
        frameNumber( 0 )
        workstatus = [True] * nWorkers # Says to writers if they have to keep working
        writers  = [ Writer( args,
                            i,
                            workstatus,
                            targets[i],
                            writeDone,
                            refreshDone,
                            flushDone,
                            grow_alphas,
                            status,
                            report,
                            status.internalStopRequest,
                            progress )
                    for i in range(nWorkers) ]
        twriters = [ Thread( target = writers[i].run , name = f"writer-{i}" )
                    for i in range(nWorkers)                                 ]

        # |> ROLLBACK >--------------------------------------------------------------------------------------------
        self.submitRollbackStep( lambda: animator.clean_up_all()    )
        self.submitRollbackStep( lambda: [ client.serviceRequest(t.deleteLater) for t in targets ] if not self.targets_deleted() else None )
        self.submitRollbackStep( lambda: [ client.serviceRequest(t.remove)      for t in targets ] if not self.targets_deleted() else None )
        # |> ROLLBACK >--------------------------------------------------------------------------------------------

        for tw in twriters:
            tw.start()

        for tw in twriters:
            tw.join()

        del writers
        del twriters

        # <| ROLLBACK <------------------------
        if self.hasToExit( status ): return
        # <| ROLLBACK <------------------------

        # Step 4: Import frames if required, else rename the target.
        # -------   <*>TAGS:    ROLLBACK (on imported frames),
        #                       SERIAL
        stepName( "" )
        frameErase()
        report( "Importing Borders" )
        # NOTE: There's a weird message which is shown by krita. ($N is a number)
        #           >>> krita.general: DEBUG: releasing of the pooled memory has been cancelled: there are still $N tiles in memory
        #       Maybe it's a bug on Krita's import routine or something similar.
        #       It also happens when I import and animations and export image on
        #       Krita (even When I don't use this plugin).
        if not client.serviceRequest( animator.import_by_basename , args.start , animator.get_exported_file_basenames() ):
            report( "Cannot import animation frames" )
            status.internalStopRequest( "[core.Borderizer]: UNABLE TO IMPORT ANIMATION FRAMES." )
        else:
            report( "Borders Imported" )
        border = args.doc.topLevelNodes()[Border.ANIMATION_IMPORT_DEFAULT_INDEX]
        border.remove()
        args.parent.addChildNode( border , args.node )
        stepDone() # (1) Import/Selection Done

        # |> ROLLBACK >-----------------------------------------------------
        self.submitRollbackStep( lambda: client.serviceRequest(border.deleteLater) )
        self.submitRollbackStep( lambda: client.serviceRequest(border.remove)      )
        # |> ROLLBACK >-----------------------------------------------------

        report( f"Removing Targets ({nWorkers} of them)" )
        for t in targets:
            client.serviceRequest(t.remove)
            client.serviceRequest(t.deleteLater)
        self.targetsDeleted = True
        stepDone() # (2) Remove temporal targets.
        border.setName( args.name )
        stepDone() # (3) Move/Rename Border Layer Done.

        # <| ROLLBACK <------------------------
        if self.hasToExit( status ): return
        # <| ROLLBACK <------------------------

        animator.clean_up_all()
        stepDone() # (4) Delete Temporal Directory.
        # ALL DONE:
        stepName( "Complete" )
        report  ( "Done!" )
        doc.setBatchmode( batchD )

        client.serviceRequest( doc.setCurrentTime , original_time )
        client.serviceRequest( doc.refreshProjection )
        client.serviceRequest( doc.waitForDone )

        kis.setBatchmode( batchK )
        self.cleanRollbackList()
        workDone()
        return

