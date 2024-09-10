import asyncio
from typing import Dict, List, Union, Any, Optional, Set
from .base_workflow import BaseWorkflow
from .workflow_name import WorkflowName
from glia.src.model.model_registry import MODEL_REGISTRY
from glia.src.service.speech_recognition_service import SpeechRecognitionService
from glia.src.schedule.schedule import Schedule
import threading
class SpeechRecognitionWorkflow(BaseWorkflow):
    """SpeechRecognitionWorkflow Class
    
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service_name = "SpeechRecognitionService"
        #self.schedule = self.schedule
       # self.service = SpeechRecognitionService(
       #        name="SpeechRecognitionService",
       #        call_model_name="Whisper",
       #        resource_manager=self.resource_manager,
       # )
        
    #    self.resource_manager = self.resource_manager
    #    if self.service is None:
    #        self.service = SpeechRecognitionService(
    #            name="SpeechRecognitionService",
    #            call_model_name="Whisper",
    #            resource_manager=self.resource_manager,
    #        )
    #    else:
    #        if isinstance(self.service, SpeechRecognitionService):
    #            pass


    async def execute(self):
        """Call the service to execute the current workflow and return the final result
        
        :return: The execution result of the current workflow
        :rtype: Any
        
        """
        #print(
        #    f"Executing component {self.name.value} with resources: {self.service.call_model_resource}, start ..."
        #)
       # self.schedule.speech_recognition_service_queue.put(self.service_priority)
        
       # await asyncio.sleep(10)
        self.process_result = await self.schedule.create_task(self.service_name,self.service_priority,self.prev_result)
        self.finished = True
       
        
        
        
       
                    
                        
            
         
      
