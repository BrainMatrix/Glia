from typing import List, Dict, Any
import importlib
import logging
from enum import Enum
import asyncio
import threading
import time


from glia.src.workflow import WorkflowName
from glia.src.workflow import BaseWorkflow
from glia.src.model.model_registry import MODEL_REGISTRY
from glia.src.resource.resource import Resource
from glia.src.resource.resource_manager import ResourceManager

from glia.src.schedule import Schedule
from concurrent.futures import ThreadPoolExecutor

import random


class monitor_man_falls_workflow(BaseWorkflow):
    """

    Some Fancy AI algorithm. We get an input image and a question, output some result.

    """

    def __init__(
        self,
        name: Enum = None,
        resource_manager: ResourceManager = None,
        prev_result: Any = None,
        schedule: Schedule = None,
    ):

        super().__init__(name, resource_manager, prev_result, schedule)
        self.resource_manager = resource_manager

        self.schedule = schedule

    # 假设这是获取传感器数据的异步函数
    async def get_sensor_data(
        self,
    ):
        await asyncio.sleep(0.1)  # 模拟异步操作
        return random.uniform(0, 1)

    # 异步摔倒处理逻辑
    async def handle_fall(
        self,
    ):
        print("处理摔倒逻辑...")
        await asyncio.sleep(1)  # 模拟异步处理过程
        print("摔倒逻辑处理完毕")

    async def __call__(self, input):
        self.prev_result = input
        await self.run(self.prev_result)

        return self.process_result

    # 异步监控摔倒的函数
    async def run(
        self,
        input,
    ):
        while not self.schedule.control_event.is_set():
            data = await self.get_sensor_data()
            if data < 0.5:
                print("警报：老人摔倒了！")
                self.schedule.control_event.set()  # 设置事件，通知其他线程停止
                await self.handle_fall()  # 处理摔倒逻辑
                self.schedule.control_event.clear()  # 清除事件，允许其他线程继续
                return
            await asyncio.sleep(1)
