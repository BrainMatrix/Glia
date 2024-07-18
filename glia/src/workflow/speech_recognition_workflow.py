import asyncio

from .base_workflow import BaseWorkflow
from .workflow_name import WorkflowName
from glia.src.model.model_registry import MODEL_REGISTRY
from glia.src.service.speech_recognition_service import SpeechRecognitionService


class SpeechRecognitionWorkflow(BaseWorkflow):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.resource_manager = self.resource_manager
        if self.service is None:
            self.service = SpeechRecognitionService(
                name="SpeechRecognitionService",
                call_model_name="Whisper",
                resource_manager=self.resource_manager,
            )
        else:
            if isinstance(self.service, SpeechRecognitionService):
                pass

    async def execute(self):
        print(
            f"Executing component {self.name.value} with resources: {self.service.call_model_resource}, start ..."
        )
        await asyncio.sleep(1)
        self.process_result = await self.service(self.prev_result)
        print(self.process_result)
        print(
            f"Executing component {self.name.value} with resources: {self.service.call_model_resource}"
        )
        return self.process_result
