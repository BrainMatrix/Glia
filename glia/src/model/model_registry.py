# Copyright (c) BrainMatrix. All rights reserved.
from enum import Enum
from .ocr_model import OCRModel
from .sr_model import SRModel
from .llm_model import LLMModel
from .tts_model import TTSModel
from .vllm_model import VLLMModel
from .sentencetransformer_model import SentenceTransformerModel

# class ModelName(Enum):
#     Parseq = OCRModel()
#     Whisper = SRModel()

#     # GPT4 = "GPT4"
#     OPENCHAT = LLMModel()

#     CHATTTS = TTSModel()
# class ModelName(Enum):
#     Parseq = "glia.src.model.ocr_model.OCRModel"
#     Whisper = "glia.src.model.sr_model.SRModel"

#     # GPT4 = "GPT4"
#     OPENCHAT = "glia.src.model.llm_model.LLMModel"

#     CHATTTS = "glia.src.model.tts_model.TTSModel"

MODEL_REGISTRY = {
    "Parseq": OCRModel,
    "Whisper": SRModel,
    "OPENCHAT": LLMModel,
    "CHATTTS": TTSModel,
    "VLLM": VLLMModel,
    "SentenceTransformer":SentenceTransformerModel
}
