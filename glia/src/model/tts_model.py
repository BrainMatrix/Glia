from .base_model import BaseModel


from PIL import Image

import asyncio


class TTSModel(BaseModel):
    """TTS Model Class"""

    def __init__(
        self,
        *args,
        **kwargs,
    ):
        """Constructor method"""
        # init_model
        self.name = "tts"
        pass

    async def __call__(self, data):
        await asyncio.sleep(1)
        text = (
            data + ",我是tts返回的结果"
            if data is not None
            else "None" + ",我是tts返回的结果"
        )
        return text
