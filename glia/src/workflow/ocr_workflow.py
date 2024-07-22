import asyncio

from .base_workflow import BaseWorkflow


class OCRWorkflow(BaseWorkflow):
    """OCRWorkflow Class
    
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        

    async def execute(self):
        """Call the service to execute the current workflow and return the final result
        
        :return: The execution result of the current workflow
        :rtype: Any
        
        """

        print(
            f"Executing component {self.name.value} with resources: {self.call_model_resources}, start ..."
        )
        await asyncio.sleep(1)
        self.process_result = self.service(self.prev_result)
        print(self.process_result)
        print(
            f"Executing component {self.name.value} with resources: {self.call_model_resources}, end ..."
        )
        return self.process_result
