import asyncio
from core.logger import Logger
from core.state_service import StateService
from core.stats import PipelineStats

class PipelineEngine:
    """
    Orchestrates the execution of multiple services in a pipeline.
    Handles queue management, state persistence, and task lifecycles.
    """
    def __init__(self, state=None, stats=None):
        self.logger = Logger()
        self.state = state or StateService()
        self.stats = stats or PipelineStats()
        self.services = []
        self.queues = []
        self.tasks = []
        self.abort_event = asyncio.Event()

    def add_service(self, service_instance):
        """Add an initialized service instance to the pipeline."""
        self.services.append(service_instance)

    async def run(self, initial_data):
        """
        Runs the pipeline with the provided initial data.
        Sets up queues and executes services as tasks.
        """
        self.abort_event.clear()
        num_services = len(self.services)
        if num_services == 0:
            self.logger.warning("No services added to the pipeline.")
            return

        # Create queues: S1 -> Q1 -> S2 -> Q2 -> ... -> SN
        # The number of queues is num_services. 
        # Queues[i] is the INPUT for Services[i].
        # Services[i] outputs to Queues[i+1].
        self.queues = [asyncio.Queue(maxsize=1000) for _ in range(num_services)]
        
        # Start state periodic save in background
        state_save_task = asyncio.create_task(self.state.start_periodic_save())

        # Launch services
        self.tasks = []
        for i, service in enumerate(self.services):
            in_q = self.queues[i]
            # Output of service i goes to input of service i+1
            out_q = self.queues[i+1] if i + 1 < num_services else None
            
            task = asyncio.create_task(
                service.run(in_q, out_q, abort_event=self.abort_event),
                name=f"Task-{service.name}"
            )
            self.tasks.append(task)

        # Feed initial data to the first service
        first_q = self.queues[0]
        for item in initial_data:
            await first_q.put(item)
        await first_q.put(None) # End of Stream marker

        self.logger.info(f"Pipeline running with {num_services} services.")

        # Monitoring task to update queue sizes in stats (simplified mapping)
        async def monitor_queues():
            try:
                while not self.abort_event.is_set():
                    q_stats = {}
                    # Attempt to map to known stat fields if possible
                    mapping = ["q_dork_size", "q_url_size", "q_valid_size", "q_vuln_size"]
                    for i, q in enumerate(self.queues):
                        if i < len(mapping):
                            q_stats[mapping[i]] = q.qsize()
                        else:
                            q_stats[f"q_extra_{i}_size"] = q.qsize()
                    
                    self.stats.update(**q_stats)
                    await asyncio.sleep(1)
            except asyncio.CancelledError:
                pass

        monitor_task = asyncio.create_task(monitor_queues())

        # Wait for all service tasks to complete
        try:
            await asyncio.gather(*self.tasks)
        except Exception as e:
            self.logger.critical(f"Pipeline Engine fatal error: {e}")
            self.abort_event.set()
        finally:
            monitor_task.cancel()
            state_save_task.cancel()
            await self.state.shutdown()
            self.logger.success("Pipeline Engine execution finished.")

    def stop(self):
        """Signal the pipeline to stop immediately."""
        self.abort_event.set()
        self.logger.warning("Pipeline stop signal issued.")
