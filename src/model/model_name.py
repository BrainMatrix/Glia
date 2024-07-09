# Copyright (c) BrainMatrix. All rights reserved.
from enum import Enum
from .ocr_model import OCRModel
from .sr_model import SRModel
from .llm_model import LLMModel
from .tts_model import TTSModel


# class ModelName(Enum):
#     Parseq = OCRModel()
#     Whisper = SRModel()

#     # GPT4 = "GPT4"
#     OPENCHAT = LLMModel()

#     CHATTTS = TTSModel()
class ModelName(Enum):
    Parseq = "src.model.ocr_model.OCRModel"
    Whisper = "src.model.sr_model.SRModel"

    # GPT4 = "GPT4"
    OPENCHAT = "src.model.llm_model.LLMModel"

    CHATTTS = "src.model.tts_model.TTSModel"
