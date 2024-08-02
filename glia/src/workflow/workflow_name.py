# Copyright (c) BrainMatrix. All rights reserved.
from enum import Enum


class WorkflowName(Enum):
    """The `WorkflowName` enum class defines various workflow names.
    
    :cvar MAIN: Main Workflow, value is "Main"
    :cvar SUB_1: Sub Workflow 1, value is "Sub1"
    :cvar SUB_2: Sub Workflow 2, value is "Sub2"
    :cvar SUB_3: Sub Workflow 3, value is "Sub3"
    :cvar SUB_1_1: The sub-workflow of Sub Workflow 1, value is "Sub11"
    :cvar OCR: OCR Workflow, value is "OCR"
    :cvar LLM: LLM Workflow, value is "LLM"
    :cvar STRING_TOOLS: String Tools Workflow, value is "StringTools"
    :cvar SPEECH_RECOGNITION: Speech Recognition Workflow, value is "SpeechRecognition"
    :cvar TEXT_TO_SPEECH: Text to Speech Workflow, value is "TTS"
    :cvar Monitor: Monitor Workflow, value is "Monitor"
    
    """
    MAIN = "Main"
    MAIN0 = "Main0"
    MAIN3 = "MAIN3"
    MAIN2 = "MAIN2"
    MAIN1 = "MAIN1"
    SUB_1 = "Sub1"
    SUB_2 = "Sub2"
    SUB_3 = "Sub3"
    SUB_1_1 = "Sub11"
    OCR = "OCR"
    LLM = "LLM"
    STRING_TOOLS = "StringTools"
    SPEECH_RECOGNITION = "SpeechRecognition"
    TEXT_TO_SPEECH = "TTS"
    Monitor = "Monitor"
