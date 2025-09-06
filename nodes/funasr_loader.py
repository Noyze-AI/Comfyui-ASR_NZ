import os
import folder_paths
import importlib.util
from typing import Dict, List, Tuple, Union, Optional

from ..models.funasr_models import FunASRModelManager
from ..engines.funasr_engine import FunASREngine
from ..utils.logger import Logger

class FunASRModelLoader:
    """
    FunASR模型加载节点
    """    
    def __init__(self):
        self.logger = Logger("FunASRLoader")
    
    @staticmethod
    def _check_dependencies():
        """检查必要的依赖是否已安装"""
        funasr_spec = importlib.util.find_spec("funasr")
        huggingface_hub_spec = importlib.util.find_spec("huggingface_hub")
        
        missing_deps = []
        if funasr_spec is None:
            missing_deps.append("funasr>=0.8.0")
        if huggingface_hub_spec is None:
            missing_deps.append("huggingface_hub>=0.16.0")
            
        if missing_deps:
            return False, missing_deps
        return True, []
    
    @classmethod
    def INPUT_TYPES(cls):
        # 获取模型目录
        model_dir = os.path.join(folder_paths.models_dir, 'ASR', 'FunASR')
        os.makedirs(model_dir, exist_ok=True)
        
        # 创建模型管理器
        model_manager = FunASRModelManager(model_dir)
        
        # 获取可用模型列表
        available_models = model_manager.get_available_models()
        model_choices = list(available_models.keys())
        
        return {
            "required": {
                "model_id": (model_choices, {
                    "default": model_choices[0] if model_choices else "paraformer-zh"
                }),
                "enable_vad": (["True", "False"], {
                    "default": "True"
                }),
            },
            "optional": {
                "vad_model": (["fsmn-vad"], {
                    "default": "fsmn-vad"
                }),
            }
        }
    
    RETURN_TYPES = ("FUNASR_MODEL",)
    RETURN_NAMES = ("funasr_model",)
    FUNCTION = "load_model"
    CATEGORY = "NOYZE"
    
    def load_model(self, model_id: str, enable_vad: str = "True", vad_model: str = "fsmn-vad") -> Tuple[FunASREngine]:
        """
        加载FunASR模型
        
        Args:
            model_id: 模型ID
            enable_vad: 是否启用VAD模型
            vad_model: VAD模型类型（仅支持fsmn-vad）
            
        Returns:
            Tuple[FunASREngine]: FunASR引擎对象
        """
        # 检查必要的依赖是否已安装
        deps_ok, missing_deps = self._check_dependencies()
        if not deps_ok:
            deps_str = " ".join(missing_deps)
            error_msg = f"请安装必要的依赖: pip install -U {deps_str}\n"
            error_msg += "FunASR模型加载需要ModelScope和FunASR库支持"
            raise ImportError(error_msg)
            
        # 获取模型目录
        model_dir = os.path.join(folder_paths.models_dir, 'ASR', 'FunASR')
        os.makedirs(model_dir, exist_ok=True)
        
        # 创建模型管理器
        model_manager = FunASRModelManager(model_dir)
        
        try:
            # 获取模型路径
            model_path = model_manager.get_model_path(model_id)
            
            # 确定模型类型
            model_type = 'paraformer'
            if 'vad' in model_id:
                model_type = 'paraformer-vad'
            
            # 处理VAD配置（仅支持fsmn-vad）
            enable_vad_bool = enable_vad == "True"
            vad_model_path = None
            
            if enable_vad_bool:
                # 强制使用fsmn-vad
                vad_model_path = "fsmn-vad"
            
            # FunASR配置已设置
            
            # 创建并返回FunASR引擎
            engine = FunASREngine(
                model_path=model_path, 
                model_type=model_type,
                vad_model_path=vad_model_path,
                enable_vad=enable_vad_bool
            )
            return (engine,)
            
        except ImportError as e:
            # 依赖导入错误
            logger = Logger("FunASRLoader")
            logger.error(f"依赖导入错误: {e}")
            raise ImportError(f"请安装FunASR: pip install -U funasr>=0.8.0 modelscope>=1.4.2")
            
        except FileNotFoundError as e:
            # 模型文件不存在
            logger = Logger("FunASRLoader")
            logger.error(f"模型文件不存在: {e}")
            raise FileNotFoundError(f"模型文件不存在，请确保已下载模型或检查网络连接")
            
        except Exception as e:
            # 其他错误
            logger = Logger("FunASRLoader")
            logger.error(f"加载FunASR模型失败: {e}")
            error_msg = f"加载FunASR模型失败: {e}\n"
            error_msg += "可能的原因:\n"
            error_msg += "1. 网络连接问题\n"
            error_msg += "2. 模型文件损坏\n"
            error_msg += "3. 依赖版本不兼容\n"
            error_msg += "请尝试重新安装依赖: pip install -U funasr>=0.8.0 modelscope>=1.4.2"
            raise RuntimeError(error_msg)