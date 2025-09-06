from abc import ABC, abstractmethod
from typing import Dict, List, Tuple, Union, Optional

class ASREngine(ABC):
    """
    抽象基类，定义ASR引擎的接口
    """
    
    @abstractmethod
    def transcribe(self, audio_data, **kwargs) -> str:
        """
        将音频转换为文本
        
        Args:
            audio_data: 音频数据
            **kwargs: 其他参数
            
        Returns:
            str: 转录的文本
        """
        pass
    
    @abstractmethod
    def transcribe_with_timestamps(self, audio_data, **kwargs) -> List[Dict]:
        """
        将音频转换为带时间戳的文本
        
        Args:
            audio_data: 音频数据
            **kwargs: 其他参数
            
        Returns:
            List[Dict]: 包含文本和时间戳的字典列表
        """
        pass

from .funasr_engine import FunASREngine
from .whisper_engine import WhisperEngine

__all__ = ['ASREngine', 'FunASREngine', 'WhisperEngine']