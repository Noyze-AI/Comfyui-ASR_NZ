import os
import json
import importlib.util
from typing import Dict, List, Optional

class WhisperModelManager:
    """
    Whisper模型管理器，负责模型的下载和加载
    """
    
    @staticmethod
    def _check_whisper():
        """检查whisper是否已安装"""
        return importlib.util.find_spec("whisper") is not None
    
    # 可用的Whisper模型列表
    AVAILABLE_MODELS = {
        'tiny': {
            'name': 'tiny',
            'description': 'Tiny模型 (39M参数)',
            'size': '75MB'
        },
        'tiny.en': {
            'name': 'tiny.en',
            'description': 'Tiny模型 - 英文优化 (39M参数)',
            'size': '75MB'
        },
        'base': {
            'name': 'base',
            'description': 'Base模型 (74M参数)',
            'size': '142MB'
        },
        'base.en': {
            'name': 'base.en',
            'description': 'Base模型 - 英文优化 (74M参数)',
            'size': '142MB'
        },
        'small': {
            'name': 'small',
            'description': 'Small模型 (244M参数)',
            'size': '466MB'
        },
        'small.en': {
            'name': 'small.en',
            'description': 'Small模型 - 英文优化 (244M参数)',
            'size': '466MB'
        },
        'medium': {
            'name': 'medium',
            'description': 'Medium模型 (769M参数)',
            'size': '1.5GB'
        },
        'medium.en': {
            'name': 'medium.en',
            'description': 'Medium模型 - 英文优化 (769M参数)',
            'size': '1.5GB'
        },
        'large': {
            'name': 'large',
            'description': 'Large模型 (1550M参数)',
            'size': '3.0GB'
        },
        'large-v2': {
            'name': 'large-v2',
            'description': 'Large-v2模型 (1550M参数)',
            'size': '3.0GB'
        },
        'large-v3': {
            'name': 'large-v3',
            'description': 'Large-v3模型 (1550M参数)',
            'size': '3.0GB'
        },
    }
    
    def __init__(self, model_dir: str):
        """
        初始化Whisper模型管理器
        
        Args:
            model_dir: 模型存储目录
        """
        self.model_dir = model_dir
        os.makedirs(model_dir, exist_ok=True)
        
        # 设置环境变量，指定Whisper模型下载目录
        os.environ["WHISPER_MODEL_DIR"] = model_dir
        
        # 检查whisper是否已安装
        if not self._check_whisper():
            print("警告: whisper未安装，无法使用Whisper模型。请使用 'pip install openai-whisper' 安装。")
    
    def get_available_models(self) -> Dict:
        """
        获取可用的Whisper模型列表
        
        Returns:
            Dict: 可用模型字典
        """
        return self.AVAILABLE_MODELS
    
    def get_model_path(self, model_id: str) -> str:
        """
        获取模型路径，如果模型不存在则下载到指定目录
        
        Args:
            model_id: 模型ID
            
        Returns:
            str: 模型ID
        """
        if model_id not in self.AVAILABLE_MODELS:
            raise ValueError(f"未知的模型ID: {model_id}")
        
        # 检查whisper是否已安装
        if not self._check_whisper():
            raise ImportError("请安装whisper: pip install openai-whisper")
        
        # 获取模型名称
        model_name = self.AVAILABLE_MODELS[model_id]['name']
        
        # 检查模型是否已下载到指定目录
        model_path = os.path.join(self.model_dir, f"{model_name}.pt")
        if not os.path.exists(model_path):
            # 如果模型不存在，尝试下载
            try:
                import whisper
                print(f"正在下载Whisper模型 {model_id}，大小约 {self.AVAILABLE_MODELS[model_id]['size']}，请耐心等待...")
                # 使用download_root参数指定下载目录
                whisper.load_model(model_name, download_root=self.model_dir)
                print(f"Whisper模型下载完成")
            except Exception as e:
                raise RuntimeError(f"下载模型 {model_id} 失败: {e}")
        
        # 返回模型ID，whisper.load_model会处理路径
        return model_name
    
    def is_model_available(self, model_id: str) -> bool:
        """
        检查模型是否可用
        
        Args:
            model_id: 模型ID
            
        Returns:
            bool: 模型是否可用
        """
        if model_id not in self.AVAILABLE_MODELS:
            return False
        
        # 检查whisper是否已安装
        if not self._check_whisper():
            return False
        
        try:
            import whisper
            # 检查模型是否已下载
            model_name = self.AVAILABLE_MODELS[model_id]['name']
            model_path = os.path.join(self.model_dir, f"{model_name}.pt")
            if os.path.exists(model_path):
                return True
                
            # 尝试加载模型，如果成功则表示模型可用或可下载
            # 注意：这可能会触发模型下载
            try:
                whisper.load_model(model_name, download_root=self.model_dir)
                return True
            except Exception:
                return False
        except Exception:
            return False