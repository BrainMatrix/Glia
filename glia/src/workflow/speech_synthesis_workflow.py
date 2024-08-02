import asyncio

from .base_workflow import BaseWorkflow
from glia.src.model.model_registry import MODEL_REGISTRY
from glia.src.service.speech_synthesis_service import SpeechSynthesisService
from glia.src.schedule.schedule import Schedule

class SpeechSynthesisWorkflow(BaseWorkflow):
    """SpeechSynthesisWorkflow Class
    
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    #    self.resource_manager = self.resource_manager
    #    if self.service is None:
    #        self.service = SpeechSynthesisService(
    #            name="SpeechSynthesisService",
    #            call_model_name='CHATTTS',
    #            resource_manager=self.resource_manager,
    #        )
    #    else:
    #        if isinstance(self.service, SpeechSynthesisService):
    #            pass

    async def execute(self):
        """Call the service to execute the current workflow and return the final result
        
        :return: The execution result of the current workflow
        :rtype: Any
        
        """
        self.schedule.speech_synthesis_service_queue.put(self.service_priority)
        
        await asyncio.sleep(10)
        
        while True:
            if self.service_priority == self.schedule.speech_synthesis_service_queue.check_head_element():
                break
            
        self.service = SpeechSynthesisService(
                 name="SpeechSynthesisService",
                 call_model_name='CHATTTS',
                 resource_manager=self.resource_manager,
            )
        
        #print(
        #    f"Executing component {self.name.value} with resources: {self.service.call_model_resource}, start ..."
        #)
        #await asyncio.sleep(1)
        self.process_result = await self.service(self.prev_result)
        #print(self.process_result)
        #print(
        #    f"Executing component {self.name.value} with resources: {self.service.call_model_resource}, end ..."
        #)
        self.schedule.speech_synthesis_service_queue.get()
