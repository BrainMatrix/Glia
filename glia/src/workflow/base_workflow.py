# Copyright (c) BrainMatrix. All rights reserved.
import asyncio
from enum import Enum
from typing import Dict, List, Union, Any
from rich.console import Console

from glia.src.resource import Resource, ResourceManager
from glia.src.utils.print_table import build_tree
from glia.src.utils.model_utils import get_model_instance
from glia.src.service.base_service import BaseService
from glia.src.schedule.schedule import Schedule


class BaseWorkflow(object):
    """Workflow Base Class, containing only one service.
    
    :param name: Workflow Name, defaults to None
    :type name: Enum
    :param service: Instance object of the BaseService, defaults to None
    :type service: class:'BaseService'
    :param resource_manager: Instance object of the ResourceManager, defaults to None
    :type resource_manager: class:'ResourceManager'
    
    """
    def __init__(
        self,
        name: Enum = None,
        service_priority: int = None,
        resource_manager: ResourceManager = None,
        schedule: Schedule = None,
        service: BaseService =None,
    ):
      
        self.name = name
        self.service : BaseService = service
        self.service_priority: int = service_priority
        self.sub_workflows: Dict[Enum, BaseWorkflow] = {}
        self.branch_list : Dict[str, BaseWorkflow] = {}
        self.resource_manager: ResourceManager  = resource_manager
        self.schedule: Schedule = schedule
        self.process_result = None  # current process result
    
    
    def add_sub_workflow(self, *sub_workflows):
    #可以加一个当前workflow是否在sub_workflow字典里的判定
        for workflow in sub_workflows:
           self.sub_workflows[workflow.name] = workflow    
            
    def call_other_workflow(self, *other_workflows):
        
        for workflow in other_workflows:
            self.sub_workflows[workflow.name] = workflow #需要存放在这个字典中吗
            
            
    def recursive_call(self):
        
        self.sub_workflows[self.name] = self
        
        #以上几种调用方法，是否应放在多Workflow的类里面
        
        
    async def __loop_call__(self, times, prev_result):
        self.times=times
        self.prev_result=prev_result
        while(self.times):
            
          await self.execute()
          self.prev_result=self.process_result        
          self.times -= 1
          
        return self.process_result      
    
        

    async def __call__(self, prev_result):
        """Accept the result of the previous step, call `execute()` to run the workflow, and return the execution result.
        
        :param prev_result: Result of the Previous Step
        :type prev_result: Any
        :return: Workflow Execution Result
        :rtype: Any
        
        """
    
        self.prev_result = prev_result #将prev_result保存到实例属性self.prev_result中，供后续使用。 self.的数据为在类的生存周期中的全局数据，不加self的数据仅仅作用于功能函数执行期间
        await self.execute()
        return self.process_result

    async def execute(self):
        """Execute the Workflow
        """
        pass
  
  
    def set_branch(self, branch_name):
        
        pass
    
    def merge_branches(self, *branches_names):
        
        pass
    
    def split_branches(self, *branches_names):
        
        pass
    
    
    

    def get_resource_strategy(self):
        """Get all resource configurations of the current workflow and its sub-workflows, as well as their input data and output data.
        
        :return: Record all resource configurations of the current workflow and its sub-workflows, as well as their input data and output data
        :rtype: dict[str,Any]        
        """

        resource_strategies = {}
        resource_strategies["Workflow_Name"] = self.name.value

        if self.service is not None :
            resource_strategies["Call_Resource"] = {}

            print(
                "self.service.call_model_resource",
                type(self.service),
            )
            resource_strategies["Call_Resource"][
                self.service.call_model_name
            ] = self.service.call_model_resource.__str__()

            resource_strategies["Call_Model_Name"] = (
                self.service.call_model_name if self.service.call_model_name else None
            )
        resource_strategies["self.prev_result"] = (
            self.prev_result if self.prev_result else None
        )
        resource_strategies["self.process_result"] = (
            self.process_result if self.process_result else None
        )
        resource_strategies["SubWorkflow"] = {}
        for workflow in self.sub_workflows.values():
            resource_strategies["SubWorkflow"][
                workflow.name.value
            ] = workflow.get_resource_strategy()
        return resource_strategies

    def print_resource_strategy(self):
        """Print the resource strategy of the current workflow in a tree structure.  
              
        """
        
        resource_strategies = self.get_resource_strategy()
        console = Console()

        tree = build_tree(resource_strategies)
        console.print(tree)
