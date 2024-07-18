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

    def __init__(
        self,
        name: Enum = None,
        call_model_name: str = None,
        resource_manager: ResourceManager = None,
        prev_result: Any = None,
    ):
        self.name = name

        self.call_model_name: str = call_model_name
        self.call_model: BaseModel = MODEL_REGISTRY[call_model_name]()
        self.resource_manager: ResourceManager = resource_manager
        self.call_model_resource: Resource = self.resource_manager.models[
            self.call_model_name
        ]
        if call_model_name is not None and resource_manager is not None:
            self.setup(self.call_model, self.call_model_resource)

        self.prev_result = prev_result  # pervious process result
        self.process_result = None  # current process result

    def setup(self, model: BaseModel = None, resources: Resource = None):
        # Set resource allocation here
        # if  isinstance(self.call_model, str) and self.call_model is not None:
        #     self.call_model = get_model_instance(self.call_model)

        # self.model.to("deivce")
        try:
            pass
            # if model is not None:
        #         self.call_model_resources[model] = resources
        #     else:
        #         self.call_model_resources[f"obj_{id(self)}"] = resources
        except Exception as e:
            print(type(model))
            print(type(resources))
            print("Error in setting up resources", "Error:", e, "id(self):", id(self))

    async def __call__(self, prev_result):

        # check resource allocation
        # assert self.call_model_resources is not None, "Resource not allocated"

        # Executing workflow work
        self.prev_result = prev_result
        self.process_result = await self.execute()
        return self.process_result

    async def execute(self):

        if self.call_model is not None:
            self.process_result = self.call_model(self.prev_result)
            print(
                f"Executing workflow {self.name.value} with resources: {self.call_model_resources}"
            )
            return self.process_result
