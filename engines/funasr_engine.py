import os
import numpy as np
import importlib.util
from typing import Dict, List, Tuple, Union, Optional
import tempfile
import soundfile as sf
import json
import uuid

from . import ASREngine
from ..utils.logger import Logger

class FunASREngine(ASREngine):
    """
    FunASR引擎实现 - 使用Hugging Face方式，无需ModelScope和datasets
    """
    
    def __init__(self, model_path: str, model_type: str = 'paraformer', vad_model_path: str = None, enable_vad: bool = True):
        """
        初始化FunASR引擎
        
        Args:
            model_path: 模型路径或ModelScope模型名称
            model_type: 模型类型，默认为paraformer
            vad_model_path: VAD模型路径，用于音频分段
            enable_vad: 是否启用VAD模型，默认为True
        """
        self.model_path = model_path
        self.model_type = model_type
        self.vad_model_path = vad_model_path
        self.enable_vad = enable_vad
        self.model = None
        self.logger = Logger("FunASR")
        self._load_model()
    
    def _load_model(self):
        """
        加载FunASR模型 - 使用ModelScope方式
        """
        # 先检查必要的依赖是否已安装
        funasr_spec = importlib.util.find_spec("funasr")
        
        if funasr_spec is None:
            raise ImportError("请安装FunASR: pip install funasr>=0.8.0")
            
        modelscope_spec = importlib.util.find_spec("modelscope")
        if modelscope_spec is None:
            raise ImportError("请安装ModelScope: pip install modelscope>=1.9.5")
            
        try:
            import folder_paths
            
            # 使用ComfyUI的标准模型目录
            model_dir = os.path.join(folder_paths.models_dir, 'ASR', 'FunASR')
            os.makedirs(model_dir, exist_ok=True)
            
            # 检查本地模型路径是否存在，如果是本地路径的话
            if os.path.exists(self.model_path):
                model_path = self.model_path
            else:
                # 假设是ModelScope模型ID
                model_path = self.model_path
                
            # 导入FunASR并使用AutoModel加载模型
            from funasr import AutoModel
            
            # 设置环境变量，指定ModelScope缓存目录
            os.environ["MODELSCOPE_CACHE"] = model_dir
            
            # 获取设备信息
            try:
                import torch
                device = "cuda:0" if torch.cuda.is_available() else "cpu"
            except ImportError:
                device = "cpu"
            
            # 根据ModelScope文档配置VAD模型
            model_kwargs = {
                "model": model_path,
                "hub": "ms",  # 指定从ModelScope加载
                "device": device,
            }
            
            # 自动配置VAD和标点模型（仅支持fsmn-vad）
            if self.enable_vad:
                # 强制使用fsmn-vad模型（ModelScope推荐）
                model_kwargs["vad_model"] = "fsmn-vad"
                
                # 添加标点模型（ModelScope文档推荐配套使用）
                model_kwargs["punc_model"] = "ct-punc"
                
                # VAD相关参数配置
                model_kwargs["vad_kwargs"] = {
                    "max_single_segment_time": 60000,  # 最大分段时长60秒
                    "merge_vad": True,  # 合并VAD分割的片段
                }
            
            # 根据模型类型加载模型
            if self.model_type in ['paraformer', 'paraformer-vad']:
                self.model = AutoModel(**model_kwargs)
            else:
                raise ValueError(f"不支持的FunASR模型类型: {self.model_type}")
                

                
        except ImportError as e:
            raise ImportError(f"导入依赖失败: {e}，请检查FunASR和ModelScope安装")
        except FileNotFoundError as e:
            raise e
        except Exception as e:
            self.logger.error(f"加载FunASR模型异常: {e}")
            import traceback
            traceback.print_exc()
            raise RuntimeError(f"加载FunASR模型失败: {e}，请检查模型路径和网络连接")
    
    def transcribe(self, audio_data, **kwargs) -> str:
        """
        将音频转换为文本
        
        Args:
            audio_data: 音频数据，可以是numpy数组或音频文件路径
            **kwargs: 其他参数
            
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
                # 如果是numpy数组，需要保存为临时文件
                temp_dir = tempfile.gettempdir()
                temp_file = os.path.join(temp_dir, 'temp_audio.wav')
                sf.write(temp_file, audio_data, 16000)  # 假设采样率为16000
                audio_input = temp_file
            else:
                raise ValueError("不支持的音频数据类型")
            
            # 调用模型进行转录
            result = self.model.generate(input=audio_input, **kwargs)
            
            # 提取文本结果
            if isinstance(result, list) and len(result) > 0:
                if isinstance(result[0], dict) and 'text' in result[0]:
                    return result[0]['text']
                elif isinstance(result, str):
                    return result
            return ""
                
        except Exception as e:
            raise RuntimeError(f"FunASR转录失败: {e}")
    
    def transcribe_with_timestamps(self, audio_data, batch_size_s: int = 300, use_smart_segmentation: bool = True, **kwargs) -> List[Dict]:
        """
        将音频转换为带时间戳的文本
        
        Args:
            audio_data: 音频数据，可以是numpy数组或音频文件路径
            batch_size_s: 批处理大小（秒），用于动态批处理
            use_smart_segmentation: 是否使用智能分段
            **kwargs: 其他参数
            
        Returns:
            List[Dict]: 包含文本和时间戳的字典列表
        """
        if self.model is None:
            self._load_model()
        
        temp_file = None
        try:
            # 处理输入并计算音频时长
            if isinstance(audio_data, str):
                # 如果是文件路径，直接传递给模型并计算时长
                audio_input = audio_data
                # 计算音频文件的实际时长
                audio_info = sf.info(audio_data)
                actual_duration = audio_info.duration
            elif isinstance(audio_data, np.ndarray):
                # 如果是numpy数组，需要保存为临时文件
                temp_dir = tempfile.gettempdir()
                temp_file = os.path.join(temp_dir, f'temp_audio_{uuid.uuid4().hex}.wav')
                sf.write(temp_file, audio_data, 16000)  # 假设采样率为16000
                audio_input = temp_file
                # 计算numpy数组的时长
                actual_duration = len(audio_data) / 16000.0  # 假设采样率为16000
            else:
                raise ValueError("不支持的音频数据类型")
            
            # 设置推理参数
            inference_kwargs = {
                'batch_size_s': batch_size_s,  # 动态批处理大小
            }
            
            # 合并用户提供的参数
            inference_kwargs.update(kwargs)
            
            # 调用模型进行转录
            result = self.model.generate(input=audio_input, **inference_kwargs)
            
            # 提取带时间戳的结果
            segments = []
            
            if result is None:
                return segments
            
            # 处理FunASR的结果格式
            if isinstance(result, list) and len(result) > 0:
                result = result[0]  # 取第一个结果
            
            # 处理结果中的时间戳信息
            if isinstance(result, dict):
                text = result.get('text', '')
                timestamp = result.get('timestamp', [])
                
                # 如果有时间戳信息，使用智能分段算法
                if timestamp and text and use_smart_segmentation:
                    segments = self._smart_segment_with_punctuation(text, timestamp)
                
                # 如果没有时间戳信息或不使用智能分段，尝试简单分段
                elif text:
                    segments = self._simple_segment_by_punctuation(text, actual_duration)
            
            # 处理字符串结果
            elif isinstance(result, str):
                segments = self._simple_segment_by_punctuation(result, actual_duration)
            
            return segments
                
        except Exception as e:
            self.logger.error(f"转录失败: {e}")
            raise RuntimeError(f"FunASR带时间戳转录失败: {e}")
        finally:
            # 清理临时文件
            if temp_file and os.path.exists(temp_file):
                try:
                    os.remove(temp_file)
                except Exception as e:
                    pass
    
    def _smart_segment_with_punctuation(self, text, word_timestamps, text_length=8):
        """
        使用智能分段算法，参考ComfyUI-AV-FunASR的实现
        根据标点符号和时间戳信息进行分段
        """
        try:
            import jieba
            import re
            
            # 使用jieba分词
            words = jieba.lcut(text)
            
            segments = []
            
            # 标点符号列表
            punctuation = "，。；！？!,;.?:()（）"
            
            def find_punctuation_indices(word_list):
                """查找标点符号位置"""
                for i, word in enumerate(word_list):
                    if word in punctuation:
                        return i
                return -1
            
            def remove_sentence_punctuation(sentence):
                """去除句子中的断句符号"""
                for p in punctuation:
                    sentence = sentence.replace(p, ' ')
                return sentence.strip()
            
            word_index = 0
            
            while len(words) > 0 and word_index < len(word_timestamps):
                if len(words) < 10:
                    # 剩余词语不足10个，全部作为一段
                    segment_words = words
                    words = []
                else:
                    # 查找标点符号位置
                    punctuation_index = find_punctuation_indices(words)
                    
                    if punctuation_index > 10 or punctuation_index <= 2:
                        # 标点符号位置不合适，使用固定长度
                        segment_words = words[:text_length]
                        words = words[text_length:]
                    else:
                        # 使用标点符号位置分割
                        segment_words = words[:punctuation_index + 1]  # 包含标点符号
                        words = words[punctuation_index + 1:]
                
                # 计算这一段对应的时间戳范围
                segment_text = ''.join(segment_words)
                segment_length = len(segment_text.replace(' ', ''))
                
                # 估算需要多少个词语时间戳
                estimated_word_count = min(segment_length, len(word_timestamps) - word_index)
                if estimated_word_count <= 0:
                    break
                
                # 获取时间戳
                start_timestamp = word_timestamps[word_index]
                end_index = min(word_index + estimated_word_count - 1, len(word_timestamps) - 1)
                end_timestamp = word_timestamps[end_index]
                
                # 转换时间戳格式
                if isinstance(start_timestamp, list) and len(start_timestamp) >= 2:
                    start_time = start_timestamp[0] / 1000.0  # 毫秒转秒
                    end_time = end_timestamp[1] / 1000.0
                else:
                    # 如果时间戳格式不对，使用索引估算
                    start_time = word_index * 0.5  # 假设每个词0.5秒
                    end_time = (word_index + estimated_word_count) * 0.5
                
                # 清理文本
                clean_text = remove_sentence_punctuation(segment_text)
                if clean_text:
                    segments.append({
                        'start': start_time,
                        'end': end_time,
                        'text': clean_text
                    })
                
                word_index += estimated_word_count
            
            return segments
            
        except Exception as e:
            # 降级到简单分段
            return self._simple_segment_by_punctuation(text, 300)
    
    def _simple_segment_by_punctuation(self, text, total_duration):
        """
        使用标点符号进行简单分段
        """
        import re
        
        # 使用标点符号分割文本
        sentences = re.split(r'[。！？；.!?;]', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        segments = []
        if sentences:
            duration_per_sentence = total_duration / len(sentences)
            for i, sentence in enumerate(sentences):
                start_time = i * duration_per_sentence
                end_time = (i + 1) * duration_per_sentence
                
                segments.append({
                    'start': start_time,
                    'end': end_time,
                    'text': sentence
                })
        
        return segments