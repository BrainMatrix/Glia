import asyncio

from .base_workflow import BaseWorkflow
from .workflow_name import WorkflowName
from glia.src.model.model_registry import MODEL_REGISTRY
from glia.src.service.speech_recognition_service import SpeechRecognitionService
from glia.src.schedule.schedule import Schedule

class SpeechRecognitionWorkflow(BaseWorkflow):
    """SpeechRecognitionWorkflow Class
    
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.schedule = self.schedule
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
        self.schedule.speech_recognition_service_queue.put(self.service_priority)
        
        await asyncio.sleep(10)
        
       # print("当前队列元素个数为"+str(self.schedule.speech_recognition_service_queue.qsize()))
        
       # print("当前的线程的workflow的优先级为"+str(self.service_priority))
        
       # print("当前队首优先级为"+str(self.schedule.speech_recognition_service_queue.check_head_element()))
        
        while True:
            if self.service_priority == self.schedule.speech_recognition_service_queue.check_head_element():
                break
        self.service = SpeechRecognitionService(
               name="SpeechRecognitionService",
               call_model_name="Whisper",
               resource_manager=self.resource_manager,
        )
        
        #await asyncio.sleep(1)
        self.process_result = await self.service(self.prev_result)
        #print(self.process_result)
        #print(
        #    f"Executing component {self.name.value} with resources: {self.service.call_model_resource}"
        #)
        self.schedule.speech_recognition_service_queue.get()
        
       # print("当前队列元素个数为"+str(self.schedule.speech_recognition_service_queue.qsize()))
        
       # print("当前的线程的workflow的优先级为"+str(self.service_priority))
        
       # print("当前队首优先级为"+str(self.schedule.speech_recognition_service_queue.check_head_element()))
