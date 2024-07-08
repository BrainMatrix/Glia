# Copyright (c) BrainMatrix. All rights reserved.
import asyncio
import unittest

from src.component.base_component import BaseComponent
from src.component.component_name import ComponentName
from src.component.resource import Resource


class MainComponent(BaseComponent):
    def __init__(self, name):
        super().__init__(name)

    async def execute(self):
        print(
            f"Executing component {self.name} with resources: {self.resources.__dict__}, start ..."
        )
        await asyncio.sleep(
            1
        )  # time.sleep Asynchronous blocking  ; asyncio.sleep  Asynchronous non-blocking
        print(
            f"Executing component {self.name} with resources: {self.resources.__dict__}, end ..."
        )


class SubComponent1(BaseComponent):

    def __init__(self, name):
        super().__init__(name)

    async def execute(self):
        print(
            f"Executing component {self.name} with resources: {self.resources.__dict__}, start ..."
        )
        await asyncio.sleep(2)
        print(
            f"Executing component {self.name} with resources: {self.resources.__dict__}, end ..."
        )


class SubComponent2(BaseComponent):

    def __init__(self, name):
        super().__init__(name)

    async def execute(self):
        print(
            f"Executing component {self.name} with resources: {self.resources.__dict__}, start ..."
        )
        await asyncio.sleep(4)
        print(
            f"Executing component {self.name} with resources: {self.resources.__dict__}, end ..."
        )


class SubComponent3(BaseComponent):

    def __init__(self, name):
        super().__init__(name)

    async def execute(self):
        print(
            f"Executing component {self.name} with resources: {self.resources.__dict__}, start ..."
        )
        await asyncio.sleep(5)
        print(
            f"Executing component {self.name} with resources: {self.resources.__dict__}, end ..."
        )


class SubComponent11(BaseComponent):
    def __init__(self, name):
        super().__init__(name)

    async def execute(self):
        print(
            f"Executing component {self.name} with resources: {self.resources.__dict__}, start ..."
        )
        await asyncio.sleep(3)
        print(
            f"Executing component {self.name} with resources: {self.resources.__dict__}, end ..."
        )


class TestComponent(unittest.TestCase):
    def test_component_execution(self):
        main_component = MainComponent(ComponentName.MAIN)
        sub_component1 = SubComponent1(ComponentName.SUB1)
        sub_component2 = SubComponent2(ComponentName.SUB2)
        sub_component3 = SubComponent3(ComponentName.SUB3)
        sub_component11 = SubComponent11(ComponentName.SUB11)

        # Adding subcomponents
        main_component.add_sub_component(sub_component1, sub_component2, sub_component3)
        sub_component1.add_sub_component(sub_component11)

        # Setting up resources
        main_component.setup(
            Resource(use_cpu=True, use_gpu=False, use_multi_gpu_ids=[0, 1])
        )
        main_component.setup(
            Resource(use_cpu=False, use_gpu=True, use_multi_gpu_ids=[])
        )
        sub_component1.setup(
            Resource(use_cpu=True, use_gpu=False, use_multi_gpu_ids=[])
        )
        sub_component2.setup(
            Resource(use_cpu=False, use_gpu=True, use_multi_gpu_ids=[2, 3])
        )
        sub_component3.setup(
            Resource(use_cpu=True, use_gpu=False, use_multi_gpu_ids=[])
        )
        sub_component11.setup(
            Resource(use_cpu=False, use_gpu=True, use_multi_gpu_ids=[0, 1, 2])
        )

        # Calling the main component
        asyncio.run(main_component())


if __name__ == "__main__":

    unittest.main()
