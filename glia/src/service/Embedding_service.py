import asyncio

from .base_service import BaseService


class EmbeddingService(BaseService):
    """Embedding Service Class
    
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def execute(self):
        """Call the model to execute the current service and return the final result
        
        :return: The execution result of the current service
        :rtype: Any
        
        """
 
        self.process_result = self.call_model(self.prev_result)