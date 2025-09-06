import os
from typing import Dict, List, Tuple, Union, Optional

from ..engines.funasr_engine import FunASREngine

class AudioVideoToText:
    """
    音频转文本节点
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "audio": ("AUDIO",),
            },
            "optional": {
                "funasr_model": ("FUNASR_MODEL",),
                "whisper_model": ("WHISPER_MODEL",),
            }
        }
    
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("text",)
    FUNCTION = "transcribe"
    CATEGORY = "NOYZE"
    
    def transcribe(self, audio: Dict, funasr_model: Optional[FunASREngine] = None, whisper_model: Optional[Dict] = None) -> Tuple[str]:
        """
        将音频转换为文本
        
        Args:
            audio: 音频对象
            funasr_model: FunASR模型对象
            whisper_model: Whisper模型对象
            
        Returns:
            Tuple[str]: 转录的文本
        """
        if funasr_model is None and whisper_model is None:
            raise ValueError("请至少提供一个ASR模型（FunASR或Whisper）")
        
        # 获取音频数据
        audio_data = audio['data']
        sample_rate = audio['sample_rate']
        
        # 优先使用Whisper模型（如果提供）
        if whisper_model is not None:
            engine = whisper_model['engine']
            params = whisper_model['params']
            
            # 调用Whisper引擎进行转录
            text = engine.transcribe(audio_data, **params)
            return (text,)
        
        # 使用FunASR模型
        if funasr_model is not None:
            # 调用FunASR引擎进行转录
            text = funasr_model.transcribe(audio_data)
            return (text,)
        
        # 不应该到达这里
        return ("",)