import asyncio
from typing import Dict, List, Union, Any, Optional, Set
from .base_workflow import BaseWorkflow
from .workflow_name import WorkflowName
from glia.src.model.model_registry import MODEL_REGISTRY
import threading
from glia.src.service.llm_service import LLMService
from glia.src.schedule.schedule import Schedule



class VLLMWorkflow(BaseWorkflow):
    """VLLMWorkflow Class
    """

    def __init__(self,
                 condition = None,
                 temperature = 0.5,
                 stream  = False,
                 api_key = None,
                 url = None,
                 **kwargs):
        super().__init__(**kwargs)
        self.service_name = "VLLMService"#该名称需要与schedule中的各个service name保持一致
        self.condition = condition
        self.temperature = temperature
        self.stream  = stream
        self.api_key = api_key
        self.url = url#这个值传进来没啥大用啊。。。。
   
    
    def __call__(self, prev_result: any = None,*args, **kwargs):
        
        if self.prev_result == []:#非拓扑流上的数据来源
            self.independent_prev_result = prev_result
            #继续对数据处理
            if type(self.independent_prev_result) == List:#传参进来的是message
               self.execute(messages=self.independent_prev_result)
            else: 
               self.execute(prompt=self.independent_prev_result)
       
            return self.process_result
        
        else:#说明是拓扑流上的数据来源
        #处理多个数据来源的self.prev_result，最终合并成一个self.independent_prev_result
            self.independent_prev_result = self.prev_result[0]#暂时默认
            #继续对数据处理
            if type(self.independent_prev_result) == list:#传参进来的是message
               self.execute(messages=self.independent_prev_result)
            else: 
               self.execute(prompt=self.independent_prev_result)
        
            return self.process_result



    def execute(self, prompt=None,
                messages=None, 
                *args, **kwargs):
        
        assert prompt is not None or messages is not None, "You must provide prompt or messages."
    
        content = {
            "model": self.schedule.service_object[self.service_name].call_model.model_name,
            "messages": [
               {
                "role": "user",
                "content": prompt
               }
            ],
            "temperature": self.temperature
        }
    
        if self.stream:
            content["stream"] = self.stream
    
        if messages:
            content["messages"] = messages
    
        if self.condition:
            content["condition"] = self.condition

        if self.stream:
           
           self.process_result = self.schedule.create_task(self.service_name,self.service_priority,content)
           self.finished = True
           return

        else:
           self.resp = self.schedule.create_task(self.service_name,self.service_priority,content)
           self.process_result = self.resp.choices[0].message.content
           self.finished = True
           return
        