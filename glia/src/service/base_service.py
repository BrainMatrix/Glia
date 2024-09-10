# Copyright (c) BrainMatrix. All rights reserved.
import asyncio, copy
from enum import Enum
from typing import Dict, List, Union, Any
from rich.console import Console

from glia.src.resource import Resource, ResourceManager
from glia.src.utils.print_table import build_tree
from glia.src.utils.model_utils import get_model_instance
import threading
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
        self.resource_manager: ResourceManager = resource_manager
        self.process_result: any = None  # current process result
        self.prev_result: any = None
        if not self.call_model_name == None:
           self.call_model: BaseModel = MODEL_REGISTRY[self.call_model_name]()
           self.call_model_resource: Resource = self.resource_manager.models[self.call_model_name]#需要的资源
        
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
            

    def __call__(self, prev_result:any, *args, **kwargs):
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
            #当前service陷入资源分配阻塞
            if self.setup() == True:
                break
        
        self.prev_result = prev_result
        
        # Executing workflow work
        self.execute()
        #self.execute()
        
        self.release()#释放该service所占用的资源
        
        return self.process_result

            

    def execute(self, *args, **kwargs):
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
        
        
    def call_self_model(self, model_name:str, model_path:str, model_resource:Resource, prev_result:any):
        #只要不存在多个workflow访问同一个model_path，以下代码就没问题
        self.mutex = threading.Lock()#可能需要避免多线程对同一个model路径的访问启动，如果这样，可能还是需要创建消息队列,即使不创建消息队列，我们这个接口是实例化一个service，然后执行多个模型
        #资源注册
        
        if model_name not in self.resource_manager.models:
           self.resource_manager.register_model(model_name, model_resource)
        else:
            pass #说明模型已被注册
        #模型资源分配
        while True:
            #当前service陷入资源分配阻塞
            if self.resource_manager.allocate_resources(model_name) == True:
                break
            
        #执行Model
        pass
    
        #释放资源
        self.resource_manager.release_resources(model_name)
    
        return self.process_result
    