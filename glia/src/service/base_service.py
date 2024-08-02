# Copyright (c) BrainMatrix. All rights reserved.
import asyncio
from enum import Enum
from typing import Dict, List, Union, Any
from rich.console import Console

from glia.src.resource import Resource, ResourceManager
from glia.src.utils.print_table import build_tree
from glia.src.utils.model_utils import get_model_instance

from glia.src.model.model_registry import MODEL_REGISTRY
from glia.src.model.base_model import BaseModel


class BaseService(object):
    """Service Base Class
    
    :param name: Name of the Service, defaults to None
    :type name: Enum
    :param call_model_name: Name of the Called Model, defaults to None
    :type call_model_name: str
    :param resource_manager: Instance object of the ResourceManager, defaults to None
    :type resource_manager: class:'ResourceManager'
    
    """

    def __init__(
        self,
        name: Enum = None,
        call_model_name: str = None,
        resource_manager: ResourceManager = None,
    ):
        """
        Constructor method
        
        """
        self.name = name
        self.call_model_name: str = call_model_name
        self.call_model: BaseModel = MODEL_REGISTRY[self.call_model_name]()
        self.resource_manager: ResourceManager = resource_manager
        self.call_model_resource: Resource = self.resource_manager.models[self.call_model_name]#需要的资源
        self.process_result = None  # current process result
        
       # if call_model_name is not None and resource_manager is not None:
       #     self.setup(self.call_model, self.call_model_resource)

       

    def setup(self):
    #def setup(self, model: BaseModel = None, resources: Resource = None):
        """Set resource allocation 
        
        :param model: Instance object of the BaseModel, defaults to None
        :type model: class:'BaseModel'
        :param resources: Instance object of the Resource, defaults to None
        :type resources: class:'Resource'
        
        """
        # Set resource allocation here
        # if  isinstance(self.call_model, str) and self.call_model is not None:
        #     self.call_model = get_model_instance(self.call_model)

        # self.model.to("deivce")
        ##try:
           ## pass
            # if model is not None:
        #         self.call_model_resources[model] = resources
        #     else:
        #         self.call_model_resources[f"obj_{id(self)}"] = resources
        ##except Exception as e:
            ##print(type(model))
            ##print(type(resources))
            ##print("Error in setting up resources", "Error:", e, "id(self):", id(self))
        
        return self.resource_manager.allocate_resources(self.call_model_name)
        
            
    def release(self):
        
        self.resource_manager.release_resources(self.call_model_name)
            

    async def __call__(self, prev_result):
        """
        Accept the result of the previous step, call `execute()` to run the service, and return the execution result
              
        :param prev_result: Result of the Previous Step
        :type prev_result: Any
        :return: Service Execution Result
        :rtype: Any
        """

        # check resource allocation
        # assert self.call_model_resources is not None, "Resource not allocated"
        
        #进行资源的分配
        
        while True:
            #当前service陷入阻塞
            if self.setup() == True:
                break
        
        # Executing workflow work
        self.prev_result = prev_result
        await self.execute()
        
        self.release()#释放该service所占用的资源
        
        return self.process_result

            

    async def execute(self):
        pass
        # """实例化一个Model模型,执行service,返回执行结果
          
        # :return: service 执行结果
        # :rtype: 任意类型
        # """
        # if self.call_model is not None:
        #     self.process_result = self.call_model(self.prev_result)
        #     print(
        #         f"Executing service {self.name} with resources: {self.call_model_resource}"
        #     )
        #     return self.process_result
