# Copyright (c) BrainMatrix. All rights reserved.
import asyncio
import json

from typing import List, Dict, Any
import importlib
import logging
from enum import Enum

from src.resource import Resource
from src.model.model_name import ModelName
from src.component import BaseComponent
from src.resource import ResourceManager


class BaseWorkflow(object):

    def __init__(
        self,
        workflow_name,
        components: List[BaseComponent],
        resource_manager: ResourceManager = None,
    ):
        self.workflow_name = workflow_name
        self.components = components
        self.resource_manager = resource_manager
        for i in range(len(self.components) - 1):
            self.components[i].add_sub_component(self.components[i + 1])
        self.head_component = self.components[0]
        self.set_up()  # allocate resources

    def get_model_instance(self, model_name: str):
        model_path_list = model_name.split(".")
        module_path = ".".join(model_path_list[:-1])
        class_name = model_path_list[-1]
        module = importlib.import_module(module_path)
        Instance = getattr(module, class_name)
        return Instance()
#添加自定义模型加载，workerflow和模型资源管理的静态分配
    def set_up(
        self,
    ):
        for component in self.components:
            if component.call_model is None or not isinstance(
                component.call_model, str
            ):
                continue
            model_name: Enum = component.call_model_name
            use_cpu = component.call_model_resources[model_name].use_cpu
            use_gpu = component.call_model_resources[model_name].use_gpu
            use_multi_gpu_ids = component.call_model_resources[
                model_name
            ].use_multi_gpu_ids
            if use_cpu == True:
                component.call_model = self.get_model_instance(component.call_model)
                logging.info(f"Component {component.name.value} is using CPU resources")
            elif use_gpu == True and len(use_multi_gpu_ids) == 0:
                component.call_model = self.get_model_instance(component.call_model)
                logging.info(f"Component {component.name.value} is using GPU resources")
            elif use_gpu == True and len(use_multi_gpu_ids) > 0:
                component.call_model = self.get_model_instance(component.call_model)
                logging.info(
                    f"Component {component.name.value} is using Multi-GPU resources"
                )
            self.resource_manager.allocate_resources(model_name)

    async def __call__(self, data) -> Any:

        await self.run(data)

    async def run(self, data) -> Dict[str, Any]:

        await self.head_component(data)
