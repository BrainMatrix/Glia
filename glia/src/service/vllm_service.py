import asyncio

from .base_service import BaseService


class VLLMService(BaseService):
    """VLLM Model Service Class
    
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def execute(self):
        """Call the model to execute the current service and return the final result
        
        :return: The execution result of the current service
        :rtype: Any
        
        """
      #  print(
      #      f"Executing service {self.name} with resources: {self.call_model_resource}, start ..."
      #  )
     
        self.process_result = self.call_model(self.prev_result)