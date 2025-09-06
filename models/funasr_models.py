import os
import json
import importlib.util
from typing import Dict, List, Optional

class FunASRModelManager:
    """
    FunASR模型管理器，负责模型的下载和加载
    """
    
    @staticmethod
    def _check_modelscope():
        """检查modelscope是否已安装"""
        return importlib.util.find_spec("modelscope") is not None
    
    # 可用的FunASR模型列表 - ModelScope版本
    AVAILABLE_MODELS = {
        'paraformer-zh': {
            'name': 'damo/speech_paraformer-large_asr_nat-zh-cn-16k-common-vocab8404-pytorch',
            'description': '中文语音识别模型，带时间戳输出，非实时',
            'size': '900M'
        },
        'paraformer-zh-online': {
            'name': 'damo/speech_paraformer_asr_nat-zh-cn-16k-common-vocab8404-online',
            'description': '中文流式语音识别模型，实时',
            'size': '900M'
        },
        'paraformer-zh-spk': {
            'name': 'damo/speech_paraformer-large-vad-punc_asr_nat-zh-cn-16k-common-vocab8404-pytorch',
            'description': 'Paraformer中文语音识别模型（带说话人分离），带时间戳输出，非实时',
            'size': '900M'
        },
        'paraformer-en': {
            'name': 'damo/speech_paraformer-large_asr_nat-en-16k-common-vocab10020-pytorch',
            'description': 'Paraformer英文语音识别模型，带时间戳输出，非实时',
            'size': '900M'
        },
    }
    
    def __init__(self, model_dir: str):
        """
        初始化FunASR模型管理器
        
        Args:
            model_dir: 模型存储目录
        """
        self.model_dir = model_dir
        os.makedirs(model_dir, exist_ok=True)
        
        # 检查modelscope是否已安装
        if not self._check_modelscope():
            print("警告: modelscope未安装，无法自动下载模型。请使用 'pip install modelscope' 安装。")
    
    def get_available_models(self) -> Dict:
        """
        获取可用的FunASR模型列表
        
        Returns:
            Dict: 可用模型字典
        """
        return self.AVAILABLE_MODELS
    
    def get_model_path(self, model_id: str) -> str:
        """
        获取模型路径，如果模型不存在则下载
        
        Args:
            model_id: 模型ID
            
        Returns:
            str: 模型路径
        """
        if model_id not in self.AVAILABLE_MODELS:
            raise ValueError(f"未知的模型ID: {model_id}")
        
        model_info = self.AVAILABLE_MODELS[model_id]
        model_name = model_info['name']
        expected_path = os.path.join(self.model_dir, model_name.replace('/', '_'))
        
        # 首先检查本地是否已有模型
        if os.path.exists(expected_path) and os.path.isdir(expected_path):
            # 检查模型文件是否完整
            if os.path.exists(os.path.join(expected_path, 'configuration.json')) or \
               os.path.exists(os.path.join(expected_path, 'model.onnx')) or \
               os.path.exists(os.path.join(expected_path, 'config.json')):
                # 使用本地模型
                return expected_path
        
        # 检查modelscope是否已安装
        if not self._check_modelscope():
            # 如果modelscope未安装，返回预期的模型路径
            # 用户需要手动下载模型
            if not os.path.exists(expected_path):
                error_msg = f"错误: 模型 {model_id} 不存在于 {expected_path}\n"
                error_msg += f"请安装modelscope并重新运行: pip install -U modelscope\n"
                error_msg += f"或手动下载模型到该路径: {expected_path}"
                raise FileNotFoundError(error_msg)
            return expected_path
        
        try:
            # 尝试导入必要的依赖
            try:
                from modelscope import snapshot_download
            except ImportError as e:
                error_msg = f"导入modelscope失败: {e}\n"
                error_msg += "请确保正确安装modelscope: pip install modelscope"
                raise ImportError(error_msg)
                
            # 下载模型到指定目录
            print(f"正在从ModelScope下载模型 {model_id}，大小约 {model_info['size']}，请耐心等待...")
            # 设置cache_dir，确保模型直接下载到指定目录
            local_dir = os.path.join(self.model_dir, model_name.replace('/', '_'))
            model_path = snapshot_download(model_id=model_name, cache_dir=local_dir)
            print(f"模型下载完成: {model_path}")
            return model_path
            
        except ImportError as e:
            # 依赖导入错误，直接抛出
            raise e
        except Exception as e:
            error_msg = f"下载模型 {model_id} 失败: {e}\n"
            error_msg += "可能的原因:\n"
            error_msg += "1. 网络连接问题\n"
            error_msg += "2. ModelScope服务器问题\n"
            error_msg += "3. 磁盘空间不足\n"
            error_msg += f"请尝试手动下载模型到: {expected_path}"
            
            # 如果本地路径存在但不完整，尝试删除以避免部分下载的文件干扰
            if os.path.exists(expected_path) and not os.path.exists(os.path.join(expected_path, 'configuration.json')):
                import shutil
                try:
                    shutil.rmtree(expected_path)
                    # 已删除不完整的模型目录
                except Exception:
                    pass
                    
            raise RuntimeError(error_msg)
    
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
        
        model_info = self.AVAILABLE_MODELS[model_id]
        model_name = model_info['name']
        
        # 检查本地路径
        expected_path = os.path.join(self.model_dir, model_name.replace('/', '_'))
        return os.path.exists(expected_path)