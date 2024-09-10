import asyncio
from typing import Dict, List, Union, Any, Optional, Set
from .base_workflow import BaseWorkflow
from .workflow_name import WorkflowName
from glia.src.model.model_registry import MODEL_REGISTRY
import threading
from glia.src.service.llm_service import LLMService
from glia.src.schedule.schedule import Schedule



class EmbeddingWorkflow(BaseWorkflow):
    """EmbeddingWorkflow Class
    """

    def __init__(self,
                 **kwargs):
        super().__init__(**kwargs)
        self.service_name = "EmbeddingService"#该名称需要与schedule中的各个service name保持一致
   
    
    def __call__(self, input: any = None):#这里的list传递也是有点纠结，是否可以设计成传入的还是普通的any数据，然后list的形成放在call函数里面，
        #如果list与依赖个数不匹配，则阻塞，或者不执行execute，直接return，直到满足执行execute
        """Accept the result of the previous step, call `execute()` to run the workflow, and return the execution result.
        
        :param prev_result: Result of the Previous Step
        :type prev_result: Any
        :return: Workflow Execution Result
        :rtype: Any
        
        """
        if self.prev_result == []:#非拓扑流上的数据来源
            self.independent_prev_result = input
            self.execute()
            return self.process_result
        else:#说明是拓扑流上的数据来源
        #处理多个数据来源的self.prev_result，最终合并成一个self.independent_prev_result
            self.independent_prev_result = self.prev_result[0]#暂时默认为拓扑的workflow的数据来源只有一个
            self.execute()
            return self.process_result
        
        
    def execute(self):
        """Call the service to execute the current workflow and return the final result
        
        :return: The execution result of the current workflow
        :rtype: Any
        
        """
       
        self.process_result = self.schedule.create_task(self.service_name,self.service_priority,self.independent_prev_result)
        self.finished = True