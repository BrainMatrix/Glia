# Copyright (c) BrainMatrix. All rights reserved.
import asyncio
import json
from enum import Enum
from typing import Dict, List, Union

from src.resource import Resource, ResourceManager


class BaseComponent:

    def __init__(
        self,
        name: str = None,
        call_model_list: List[Enum] = None,
        resource_manager: ResourceManager = None,
    ):
        self.name = name
        self.call_model_resources: Dict[str, Union[Resource, None]] = dict()
        self.call_model_list = call_model_list
        self.sub_components: Dict[Enum, BaseComponent] = {}
        if call_model_list is not None and resource_manager is not None:
            for model in self.call_model_list:
                self.setup(model.value, resource_manager.models[model])
        else:
            self.setup()

    def add_sub_component(self, *sub_components):
        for component in sub_components:
            self.sub_components[component.name] = component

    def setup(self, model: str = None, resources: Resource = None):
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

    async def __call__(self):

        # check resource allocation
        # assert self.call_model_resources is not None, "Resource not allocated"

        # Executing component work
        await self.execute()

        await asyncio.gather(
            *(component() for component in self.sub_components.values())
        )

    async def execute(self):
        print(
            f"Executing component {self.name.value} with resources: {self.call_model_resources}"
        )

    def get_resource_strategy(self):
        resource_strategies = {}
        resource_strategies["Component"] = self.name.value
        resource_strategies["Call_Resources"] = {}
        for model_name, resource in self.call_model_resources.items():
            resource_strategies["Call_Resources"][model_name] = resource.__str__()
        resource_strategies["Call_Models"] = (
            ", ".join(call_model_name.value for call_model_name in self.call_model_list)
            if self.call_model_list
            else None
        )
        resource_strategies["SubComponent"] = {}
        for component in self.sub_components.values():
            resource_strategies["SubComponent"][
                component.name.value
            ] = component.get_resource_strategy()
        return resource_strategies

    def print_resource_strategy(self):
        resource_strategies = self.get_resource_strategy()
        print(resource_strategies)
        print(
            json.dumps(
                resource_strategies,
                sort_keys=True,
                indent=4,
                separators=(", ", ": "),
                ensure_ascii=False,
            )
        )
