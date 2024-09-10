import asyncio
from typing import Dict, List, Union, Any, Optional, Set
from .base_workflow import BaseWorkflow
from .workflow_name import WorkflowName
from glia.src.model.model_registry import MODEL_REGISTRY
import threading
from glia.src.service.llm_service import LLMService
from glia.src.schedule.schedule import Schedule



class LLMWorkflow(BaseWorkflow):
    """LLMWorkflow Class
    """

    def __init__(self,
                # needs: List[BaseWorkflow] = None, 
                 **kwargs):
        super().__init__(**kwargs)
        self.service_name = "LLMService"#该名称需要与schedule中的各个service name保持一致
       # self.needs: List[BaseWorkflow] = needs
       # self.service = LLMService(  #self.service是一个对象，不可以在使用的时候再创建，而单纯数据self.pre_result就可以在使用它的时候再创建
       #         name="LLMService",
       #         call_model_name="OPENCHAT",
       #         resource_manager=self.resource_manager,
       #     )

        
        #self.resource_manager = self.resource_manager
        #self.schedule=self.schedule
        #self.service_priority = self.service_priority
        #self.process_result = None
        
    #    if self.service is None:
    #        self.service = LLMService(
    #            name="LLMService",
    #            call_model_name='OPENCHAT',
    #            resource_manager=self.resource_manager,
    #        )
    #    else:
    #        if isinstance(self.service, LLMService):
    #            pass

    

    async def execute(self):
        """Call the service to execute the current workflow and return the final result
        
        :return: The execution result of the current workflow
        :rtype: Any
        
        """
       
        
        self.process_result = await self.schedule.create_task(self.service_name,self.service_priority,self.prev_result)
        self.finished = True
           
            
       