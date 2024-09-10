# Copyright (c) BrainMatrix. All rights reserved.
import asyncio
from enum import Enum
from typing import Dict, List, Union, Any, Optional, Set
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
        #resource_manager: ResourceManager = None,#因为workflow级别不再控制资源的分配，它只是单纯地传入数据，优先级，然后等待运算结果即可。
        schedule: Schedule = None,
        service: BaseService = None,#不太建议workflow中保留此属性，因为为了简化workflow，其service功能实现交给schedule处理
        service_name: str = None,#建议修改成enum类型，因为service是部分写死的，而且不建议这个属性可以用户手动输入，而是写死在特定功能的workflow初始化里面
       # needs: Optional[Set[str]] = None,#添加当前workflow的依赖关系列表 
        needs: List[any] = [],#按理说这里的列表类型应该为BaseWorkflow
        *args, **kwargs
    ):
      
        self.name = name
        self.service : BaseService = service#不建议保留此属性
        self.service_name : str = service_name#不建议该属性被用户输入
        self.service_priority: int = service_priority
        self.sub_workflows: List[BaseWorkflow] = []#是否有必要设置为Dict类型？
        self.branch_list : Dict[str, BaseWorkflow] = {}#这个功能还未实现！！！
        #self.resource_manager: ResourceManager  = resource_manager
        self.schedule: Schedule = schedule
        self.process_result: any = None  # current process result，执行结果只有一个
        self.prev_result: List[any] = []#这个参数
        self.independent_prev_result: any = None#这个输入用于workflow不在拓扑结构中的单独功能调用
       # self.needs :  Optional[Set[str]] = needs       
        self.finished: bool = False#标记这个workflow是否已经完成       
        self.needs: List[BaseWorkflow] = needs#这个属性，flow不会使用，只有在单个workflow中才有意义，nexts也是
        self.nexts: List[BaseWorkflow] = []#这个列表可以自动生成，目前的设计是禁止初始化用户添加，只能自动生成

    
    def is_needs_all_finished(self):
        if self.needs == []:
            return True
        else:
          for workflow in self.needs:
              if workflow.finished == False:
                  return False
          return True     
    
    
        
        
    async def __loop_call__(self, times, prev_result: Union[List[any], str]):
        self.times=times
        self.prev_result[0]=prev_result[0]
        while(self.times):
            
          await self.execute()
          #self.execute()
          self.prev_result[0]=self.process_result        
          self.times -= 1
          
        return self.process_result      
    
        

    def __call__(self, prev_result: any = None, *args, **kwargs):#这里的list传递也是有点纠结，是否可以设计成传入的还是普通的any数据，然后list的形成放在call函数里面，
        #如果list与依赖个数不匹配，则阻塞，或者不执行execute，直接return，直到满足执行execute
        """Accept the result of the previous step, call `execute()` to run the workflow, and return the execution result.
        
        :param prev_result: Result of the Previous Step
        :type prev_result: Any
        :return: Workflow Execution Result
        :rtype: Any
        
        """
        if self.prev_result == []:#非拓扑流上的数据来源
            self.independent_prev_result = prev_result
            self.execute()
            return self.process_result
        else:#说明是拓扑流上的数据来源
        #处理多个数据来源的self.prev_result，最终合并成一个self.independent_prev_result
            self.independent_prev_result = self.prev_result[0]#暂时默认为拓扑的workflow的数据来源只有一个
            self.execute()
            return self.process_result

    def execute(self, *args, **kwargs):
        """Execute the Workflow
        """
        pass
  
  
    def set_branch(self, branch_name):
        
        pass
    
    def merge_branches(self, *branches_names):
        
        pass
    
    def split_branches(self, *branches_names):
        
        pass
    
    @property
    def num_sub_workflow(self) -> int:
        
        return len(self.sub_workflows)
    
    def __eq__(self, other: 'BaseWorkflow') -> bool:

        return self.sub_workflows == other.sub_workflows#sub_workflow应该是一个有序的字典会比较好
    
    

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
