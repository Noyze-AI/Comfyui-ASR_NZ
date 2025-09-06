import os
import numpy as np
from typing import Dict, List, Tuple, Union, Optional

from . import ASREngine

class WhisperEngine(ASREngine):
    """
    Whisper引擎实现
    """
    
    def __init__(self, model_name: str = 'base'):
        """
        初始化Whisper引擎
        
        Args:
            model_name: 模型名称，可选值包括'tiny', 'base', 'small', 'medium', 'large', 'large-v2', 'large-v3'
        """
        self.model_name = model_name
        self.model = None
        self._load_model()
    
    def _load_model(self):
        """
        加载Whisper模型
        """
        try:
            import whisper
            import folder_paths
            
            # 使用ComfyUI的标准模型目录
            model_dir = os.path.join(folder_paths.models_dir, 'ASR', 'Whisper')
            os.makedirs(model_dir, exist_ok=True)
            
            # 设置环境变量，指定Whisper模型下载目录
            os.environ["WHISPER_MODEL_DIR"] = model_dir
            
            # 使用download_root参数指定下载目录
            self.model = whisper.load_model(self.model_name, download_root=model_dir)
        except ImportError:
            raise ImportError("请安装Whisper: pip install -U openai-whisper")
        except Exception as e:
            raise RuntimeError(f"加载Whisper模型失败: {e}")
    
    def transcribe(self, audio_data, **kwargs) -> str:
        """
        将音频转换为文本
        
        Args:
            audio_data: 音频数据，可以是numpy数组或音频文件路径
            **kwargs: 其他参数，如language, task等
            
        Returns:
            str: 转录的文本
        """
        if self.model is None:
            self._load_model()
        
        try:
            # 处理输入
            if isinstance(audio_data, str):
                # 如果是文件路径，直接传递给模型
                audio_input = audio_data
            elif isinstance(audio_data, np.ndarray):
                # Whisper可以直接处理numpy数组
                audio_input = audio_data
            else:
                raise ValueError("不支持的音频数据类型")
            
            # 设置转录参数
            transcribe_options = {}
            
            # 如果指定了语言
            if 'language' in kwargs:
                transcribe_options['language'] = kwargs['language']
            
            # 如果指定了任务（转录或翻译）
            if 'task' in kwargs:
                transcribe_options['task'] = kwargs['task']
            
            # 调用模型进行转录
            result = self.model.transcribe(audio_input, **transcribe_options)
            
            # 返回文本结果
            return result['text']
                
        except Exception as e:
            raise RuntimeError(f"Whisper转录失败: {e}")
    
    def transcribe_with_timestamps(self, audio_data, **kwargs) -> List[Dict]:
        """
        将音频转换为带时间戳的文本
        
        Args:
            audio_data: 音频数据，可以是numpy数组或音频文件路径
            **kwargs: 其他参数，如language, task等
            
        Returns:
            List[Dict]: 包含文本和时间戳的字典列表
        """
        if self.model is None:
            self._load_model()
        
        try:
            # 处理输入
            if isinstance(audio_data, str):
                # 如果是文件路径，直接传递给模型
                audio_input = audio_data
            elif isinstance(audio_data, np.ndarray):
                # Whisper可以直接处理numpy数组
                audio_input = audio_data
            else:
                raise ValueError("不支持的音频数据类型")
            
            # 设置转录参数
            transcribe_options = {}
            
            # 如果指定了语言
            if 'language' in kwargs:
                transcribe_options['language'] = kwargs['language']
            
            # 如果指定了任务（转录或翻译）
            if 'task' in kwargs:
                transcribe_options['task'] = kwargs['task']
            
            # 调用模型进行转录
            result = self.model.transcribe(audio_input, **transcribe_options)
            
            # 提取带时间戳的结果
            segments = []
            
            for segment in result['segments']:
                segment_dict = {
                    'text': segment['text'],
                    'start': segment['start'],
                    'end': segment['end']
                }
                segments.append(segment_dict)
            
            return segments
                
        except Exception as e:
            raise RuntimeError(f"Whisper带时间戳转录失败: {e}")