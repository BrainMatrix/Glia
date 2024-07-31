import asyncio

from .base_workflow import BaseWorkflow
from glia.src.model.model_registry import MODEL_REGISTRY
from glia.src.service.speech_synthesis_service import SpeechSynthesisService


class SpeechSynthesisWorkflow(BaseWorkflow):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.resource_manager = self.resource_manager
        if self.service is None:
            self.service = SpeechSynthesisService(
                name="SpeechSynthesisService",
                call_model_name="CHATTTS",
                resource_manager=self.resource_manager,
                loop=self.loop,
            )
        else:
            if isinstance(self.service, SpeechSynthesisService):
                pass

    def execute(self):

        print(
            f"Executing component {self.name.value} with resources: {self.service.call_model_resource}, start ..."
        )
        # await asyncio.sleep(1)
        self.process_result =  self.service(self.prev_result)
        
        print(self.process_result)
        print(
            f"Executing component {self.name.value} with resources: {self.service.call_model_resource}, end ..."
        )
        return self.process_result
