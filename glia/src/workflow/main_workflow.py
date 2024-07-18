# Copyright (c) BrainMatrix. All rights reserved.
import asyncio
import json

from typing import List, Dict, Any
import importlib
import logging
from enum import Enum

from glia.src.resource import Resource
from glia.src.model.model_registry import MODEL_REGISTRY
from glia.src.workflow import BaseWorkflow
from glia.src.resource import ResourceManager
from glia.src.utils.model_utils import get_model_instance

class MainWorkflow(BaseWorkflow):

    def __init__(
        self,
        workflow_name,
        workflows: List[BaseWorkflow],
        resource_manager: ResourceManager = None,
    ):
        self.workflow_name = workflow_name
        self.workflows = workflows
        self.resource_manager = resource_manager
        for i in range(len(self.workflows)):
            model_name: Enum = workflows[i].call_model_name
            if model_name is not None:
                self.workflows[i].call_model_resources[model_name] = (
                    resource_manager.models[model_name] if model_name else None
                )
            if i != len(self.workflows) - 1:
                self.workflows[i].add_sub_workflow(self.workflows[i + 1])
        self.head_workflow = self.workflows[0]
        self.set_up()  # allocate resources

    

    def set_up(
        self,
    ):
        for workflow in self.workflows:
            if workflow.call_model is None or not isinstance(
                workflow.call_model, str
            ):
                continue
            model_name: Enum = workflow.call_model_name
            use_cpu = workflow.call_model_resources[model_name].use_cpu
            use_gpu = workflow.call_model_resources[model_name].use_gpu
            use_multi_gpu_ids = workflow.call_model_resources[
                model_name
            ].use_multi_gpu_ids
            if use_cpu == True:
                workflow.call_model = get_model_instance(workflow.call_model)
                logging.info(f"Workflow {workflow.name.value} is using CPU resources")
            elif use_gpu == True and len(use_multi_gpu_ids) == 0:
                workflow.call_model = get_model_instance(workflow.call_model)
                logging.info(f"Workflow {workflow.name.value} is using GPU resources")
            elif use_gpu == True and len(use_multi_gpu_ids) > 0:
                workflow.call_model = get_model_instance(workflow.call_model)
                logging.info(
                    f"Workflow {workflow.name.value} is using Multi-GPU resources"
                )
            self.resource_manager.allocate_resources(model_name)

    async def __call__(self, data) -> Any:

        return await self.run(data)

    async def run(self, data) -> Dict[str, Any]:

        return await self.head_workflow(data)
