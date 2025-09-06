import os
import folder_paths
import importlib.util
from typing import Dict, List, Tuple, Union, Optional

from ..models.whisper_models import WhisperModelManager
from ..engines.whisper_engine import WhisperEngine
from ..utils.logger import Logger

class WhisperModelLoader:
    """
    Whisper模型加载节点
    """
    
    @staticmethod
    def _check_dependencies():
        """检查必要的依赖是否已安装"""
        whisper_installed = importlib.util.find_spec("whisper") is not None
        return whisper_installed
    
    @classmethod
    def INPUT_TYPES(cls):
        # 获取模型目录
        model_dir = os.path.join(folder_paths.models_dir, 'ASR', 'Whisper')
        os.makedirs(model_dir, exist_ok=True)
        
        # 创建模型管理器
        model_manager = WhisperModelManager(model_dir)
        
        # 获取可用模型列表
        available_models = model_manager.get_available_models()
        model_choices = list(available_models.keys())
        
        return {
            "required": {
                "model_id": (model_choices, {
                    "default": "base"
                }),
                "language": (["", "zh", "en", "ja", "de", "fr", "es", "ru", "ko", "it"], {
                    "default": ""
                }),
                "task": (["transcribe", "translate"], {
                    "default": "transcribe"
                }),
            }
        }
    
    RETURN_TYPES = ("WHISPER_MODEL",)
    RETURN_NAMES = ("whisper_model",)
    FUNCTION = "load_model"
    CATEGORY = "NOYZE"
    
    def load_model(self, model_id: str, language: str = "", task: str = "transcribe") -> Tuple[Dict]:
        """
        加载Whisper模型
        
        Args:
            model_id: 模型ID
            language: 语言代码，如zh, en等，空字符串表示自动检测
            task: 任务类型，transcribe或translate
            
        Returns:
            Tuple[Dict]: 包含Whisper引擎和参数的字典
        """
        # 检查必要的依赖是否已安装
        if not self._check_dependencies():
            raise ImportError("请安装必要的依赖: pip install -U openai-whisper")
            
        # 获取模型目录
        model_dir = os.path.join(folder_paths.models_dir, 'ASR', 'Whisper')
        os.makedirs(model_dir, exist_ok=True)
        
        # 创建模型管理器
        model_manager = WhisperModelManager(model_dir)
        
        # 获取模型名称
        model_name = model_manager.get_model_path(model_id)
        
        # 创建Whisper引擎
        try:
            engine = WhisperEngine(model_name)
            
            # 创建包含引擎和参数的字典
            model_dict = {
                'engine': engine,
                'params': {
                    'language': language if language else None,
                    'task': task
                }
            }
            
            return (model_dict,)
        except Exception as e:
            logger = Logger("WhisperLoader")
            logger.error(f"加载Whisper模型失败: {e}")
            raise RuntimeError(f"加载Whisper模型失败: {e}")