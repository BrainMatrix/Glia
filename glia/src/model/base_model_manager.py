# Copyright (c) BrainMatrix. All rights reserved.
import asyncio
import json

from glia.src.resource import Resource
from glia.src.model.model_name import ModelName


class ModelManager(object):

    def __init__(self, name=None, resources=None, call_model_list=None):
        self.name = name
        self.components = {}
