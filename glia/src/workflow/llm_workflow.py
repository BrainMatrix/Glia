import asyncio

from .base_workflow import BaseWorkflow
from .workflow_name import WorkflowName
from glia.src.model.model_registry import MODEL_REGISTRY

from glia.src.service.llm_service import LLMService


class LLMWorkflow(BaseWorkflow):
    """LLMWorkflow Class
    
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.resource_manager = self.resource_manager
        if self.service is None:
            self.service = LLMService(
                name="LLMService",
                call_model_name='OPENCHAT',
                resource_manager=self.resource_manager,
            )
        else:
            if isinstance(self.service, LLMService):
                pass

    async def execute(self):
        """Call the service to execute the current workflow and return the final result
        
        :return: The execution result of the current workflow
        :rtype: Any
        
        """
        
        print(
            f"Executing workflow {self.name.value} with resources: {self.service.call_model_resource}, start ..."
        )
        await asyncio.sleep(1)
        self.process_result = await self.service(self.prev_result)
        print(
            f"Executing workflow {self.name.value} with resources: {self.service.call_model_resource}, end ..."
        )
        return self.process_result
