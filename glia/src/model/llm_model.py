from .base_model import BaseModel


from PIL import Image

import asyncio


class LLMModel(BaseModel):
    """LLM Model Class"""

    def __init__(self, tesseract_cmd=None):
        """Constructor method"""
        # init_model
        self.name = "llm"
        pass

    async def __call__(self, data):
        """Call method to process input data and return the result.

        :param data: Input Data
        :type data: Any
        :return: Processed Text
        :rtype: Any

        """
        await asyncio.sleep(3)
        text = (
            data + ",我是llm返回的结果"
            if data is not None
            else "None" + ",我是llm返回的结果"
        )
        return text
