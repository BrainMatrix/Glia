# Copyright (c) BrainMatrix. All rights reserved.
import asyncio
from enum import Enum
from typing import Dict, List, Union, Any
from rich.console import Console

from glia.src.resource import Resource, ResourceManager
from glia.src.utils.print_table import build_tree
from glia.src.utils.model_utils import get_model_instance
from glia.src.service.base_service import BaseService


class BaseWorkflow(object):
    """Workflow Base Class, containing only one service.
    
    :param name: Workflow Name, defaults to None
    :type name: Enum
    :param service: Instance object of the BaseService, defaults to None
    :type service: class:'BaseService'
    :param resource_manager: Instance object of the ResourceManager, defaults to None
    :type resource_manager: class:'ResourceManager'
    :param priority_factor: Priority Level, defaults to 100
    :type priority_factor: int
    
    """
    def __init__(
        self,
        name: Enum = None,
        service: BaseService = None,
        resource_manager: ResourceManager = None,
        priority_factor: int = 100,
    ):
        """Constructor method
        
        """
        self.name = name
        self.service = service
        self.sub_workflows: Dict[Enum, BaseWorkflow] = {}
        self.resource_manager = resource_manager

        self.process_result = None  # current process result
        self.priority_factor = priority_factor

    def set_priority_factor(self, new_priority_factor):
        """Set the priority level of the workflow.
        
        :param new_priority_factor: Priority Level
        :type new_priority_factor: int
        
        """
        self.priority_factor = new_priority_factor

    def get_priority_factor(self):
        """Get the priority level of the workflow.
        
        :return: Current priority level of the workflow
        :rtype: int
        
        """
        return self.priority_factor

    def add_sub_workflow(self, *sub_workflows):
        """Add a new sub-workflow to the current workflow.
        
        :param sub_workflows: One or more instances of `BaseWorkflow`
        :type sub_workflows: class:'BaseWorkflow'
        
        """
        for workflow in sub_workflows:
            self.sub_workflows[workflow.name] = workflow

    async def __call__(self, prev_result):
        """Accept the result of the previous step, call `execute()` to run the workflow, and return the execution result.
        
        :param prev_result: Result of the Previous Step
        :type prev_result: Any
        :return: Workflow Execution Result
        :rtype: Any
        
        """
    
        self.prev_result = prev_result
        self.process_result = await self.execute()
        return self.process_result

    async def execute(self):
        """Execute the Workflow
        
        """
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
