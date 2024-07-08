# Copyright (c) BrainMatrix. All rights reserved.
import asyncio
import json

from src.resource import Resource
from src.model.model_name import ModelName


class BaseWorkflow:

    def __init__(self, name=None, resources=None, call_model_list=None):
        self.name = name
        self.components = {}
