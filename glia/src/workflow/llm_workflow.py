import asyncio

from .base_workflow import BaseWorkflow
from .workflow_name import WorkflowName
from glia.src.model.model_registry import MODEL_REGISTRY

from glia.src.service.llm_service import LLMService


class LLMWorkflow(BaseWorkflow):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.resource_manager = self.resource_manager
        if self.service is None:
            self.service = LLMService(
                name="LLMService",
                call_model_name="OPENCHAT",
                resource_manager=self.resource_manager,
                loop=self.loop,

            )
        else:
            if isinstance(self.service, LLMService): 
                pass

    def execute(self):

        print(
            f"Executing workflow {self.name.value} with resources: {self.service.call_model_resource}, start ..."
        )
        self.process_result = self.service(self.prev_result)
        print(self.process_result)
        print(
            f"Executing workflow {self.name.value} with resources: {self.service.call_model_resource}, end ..."
        )
        return self.process_result
