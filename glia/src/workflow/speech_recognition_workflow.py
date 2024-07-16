import asyncio

from .base_workflow import BaseWorkflow
from .workflow_name import WorkflowName
from glia.src.model.model_name import ModelName


class SpeechRecognitionWorkflow(BaseWorkflow):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    async def execute(self):
        print(
            f"Executing component {self.name.value} with resources: {self.call_model_resources}, start ..."
        )
        await asyncio.sleep(1)
        self.process_result = self.call_model(self.prev_result)
        print(self.process_result)
        print(
            f"Executing component {self.name.value} with resources: {self.call_model_resources}"
        )
        return self.process_result
