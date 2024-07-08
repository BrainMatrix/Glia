# Copyright (c) BrainMatrix. All rights reserved.
import asyncio
import json

from src.component.resource import Resource


class BaseComponent:

    def __init__(self, name=None, resources=None):
        self.name = name
        self.resources = resources if resources else Resource()
        self.sub_components = {}

    def add_sub_component(self, *sub_components):
        for component in sub_components:
            self.sub_components[component.name] = component

    def setup(self, resources):
        # Set resource allocation here
        try:
            self.resources = resources
        except Exception as e:
            print("Error in setting up resources", "Error:", e)

    async def __call__(self):
        # Executing component work
        await self.execute()

        await asyncio.gather(
            *(component() for component in self.sub_components.values())
        )

    async def execute(self):
        print(
            f"Executing component {self.name.value} with resources: {self.resources.__dict__}"
        )

    def get_resource_strategy(self):
        resource_strategies = {}
        resource_strategies["Component"] = self.name.value
        resource_strategies["Resources"] = self.resources.__dict__
        resource_strategies["SubComponent"] = {}
        for component in self.sub_components.values():
            resource_strategies["SubComponent"][
                component.name.value
            ] = component.get_resource_strategy()
        return resource_strategies

    def print_resource_strategy(self):
        resource_strategies = self.get_resource_strategy()
        print(
            json.dumps(
                resource_strategies,
                sort_keys=True,
                indent=4,
                separators=(", ", ": "),
                ensure_ascii=False,
            )
        )
