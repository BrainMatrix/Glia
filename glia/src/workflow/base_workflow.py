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

    def __init__(
        self,
        name: Enum = None,
        service: BaseService = None,
        resource_manager: ResourceManager = None,
        prev_result: Any = None,
        priority_factor: int = 100,
    ):
        self.name = name
        self.service = service
        self.sub_workflows: Dict[Enum, BaseWorkflow] = {}
        self.resource_manager = resource_manager

        self.prev_result = prev_result  # pervious process result
        self.process_result = None  # current process result
        self.priority_factor = priority_factor

    def set_priority_factor(self, new_priority_factor):
        self.priority_factor = new_priority_factor

    def get_priority_factor(self):
        return self.priority_factor

    def add_sub_workflow(self, *sub_workflows):
        for workflow in sub_workflows:
            self.sub_workflows[workflow.name] = workflow

    async def __call__(self, prev_result):
        # pass
        # Executing workflow work
        self.prev_result = prev_result
        self.process_result = await self.execute()
        print("self.process_result", self.process_result)

        await asyncio.gather(
            *(
                workflow(prev_result=self.process_result)
                for workflow in self.sub_workflows.values()
            )
        )
        return self.process_result

    async def execute(self):
        # pass
        if self.service.call_model is not None:
            self.process_result = self.call_model(self.prev_result)
            print(
                f"Executing workflow {self.name.value} with resources: {self.service.call_model_resource}"
            )
            return self.process_result

    def get_resource_strategy(self):

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
        resource_strategies = self.get_resource_strategy()
        console = Console()

        tree = build_tree(resource_strategies)
        console.print(tree)
