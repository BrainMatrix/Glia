# Copyright (c) BrainMatrix. All rights reserved.
import asyncio
from enum import Enum
from typing import Dict, List, Union, Any
from rich.console import Console

from src.resource import Resource, ResourceManager
from src.utils.print_table import build_tree


class BaseComponent(object):

    def __init__(
        self,
        name: Enum = None,
        call_model_name: Enum = None,
        resource_manager: ResourceManager = None,
        prev_result: Any = None,
    ):
        self.name = name
        self.call_model_resources: Dict[Union[str, Enum], Union[Resource, None]] = (
            dict()
        )
        self.call_model_name = call_model_name
        self.call_model: Union[str, object] = (
            call_model_name.value if call_model_name else None
        )  # model object

        self.sub_components: Dict[Enum, BaseComponent] = {}
        if call_model_name is not None and resource_manager is not None:
            self.setup(self.call_model_name, resource_manager.models[call_model_name])
        else:
            self.setup()
        self.prev_result = prev_result  # pervious process result
        self.process_result = None  # current process result

    def add_sub_component(self, *sub_components):
        for component in sub_components:
            self.sub_components[component.name] = component

    def setup(self, model: Union[str, Enum] = None, resources: Resource = None):
        # Set resource allocation here
        try:
            if model is not None:
                self.call_model_resources[model] = resources
            else:
                self.call_model_resources[f"obj_{id(self)}"] = resources
        except Exception as e:
            print(type(model))
            print(type(resources))
            print("Error in setting up resources", "Error:", e, "id(self):", id(self))

    async def __call__(self, prev_result):

        # check resource allocation
        # assert self.call_model_resources is not None, "Resource not allocated"

        # Executing component work
        self.prev_result = prev_result
        self.process_result = await self.execute()
        await asyncio.gather(
            *(
                component(prev_result=self.process_result)
                for component in self.sub_components.values()
            )
        )

    async def execute(self):

        if self.call_model is not None:
            self.process_result = self.call_model(self.prev_result)
            print(
                f"Executing component {self.name.value} with resources: {self.call_model_resources}"
            )
            return self.process_result

    def get_resource_strategy(self):
        resource_strategies = {}
        resource_strategies["Component_Name"] = self.name.value
        resource_strategies["Call_Resource"] = {}
        for model_name, resource in self.call_model_resources.items():
            resource_strategies["Call_Resource"][model_name] = resource.__str__()

        resource_strategies["Call_Model_Name"] = (
            self.call_model_name if self.call_model_name else None
        )
        resource_strategies["self.prev_result"] = (
            self.prev_result if self.prev_result else None
        )
        resource_strategies["self.process_result"] = (
            self.process_result if self.process_result else None
        )
        resource_strategies["SubComponent"] = {}
        for component in self.sub_components.values():
            resource_strategies["SubComponent"][
                component.name.value
            ] = component.get_resource_strategy()
        return resource_strategies

    def print_resource_strategy(self):
        resource_strategies = self.get_resource_strategy()
        console = Console()

        tree = build_tree(resource_strategies)
        console.print(tree)
