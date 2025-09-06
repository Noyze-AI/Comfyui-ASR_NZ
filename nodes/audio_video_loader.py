import os
import numpy as np
import folder_paths
from typing import Dict, List, Tuple, Union, Optional

from ..utils.audio_video_processor import AudioVideoProcessor

class LoadAudioVideo:
    """
    音频视频加载节点
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "audio_video": ("STRING", {
                    "default": "",
                    "multiline": False,
                }),
                "sample_rate": (["16000", "22050", "44100", "48000"], {
                    "default": "16000"
                }),
            }
        }
    
    RETURN_TYPES = ("AUDIO",)
    RETURN_NAMES = ("audio",)
    FUNCTION = "load_audio_video"
    CATEGORY = "NOYZE"
    
    UPLOAD_AUDIO_VIDEO = True
    ALLOWED_EXTENSIONS = ["wav", "mp3", "flac", "ogg", "mp4", "avi", "mov", "mkv", "webm"]
    
    @classmethod
    def IS_CHANGED(cls, audio_video, sample_rate):
        # 当文件路径变化时重新执行节点
        return audio_video
    
    def load_audio_video(self, audio_video: str, sample_rate: str) -> Tuple[Dict]:
        """
        加载音频或视频文件
        
        Args:
            audio_video: 音频或视频文件路径
            sample_rate: 采样率
            
        Returns:
            Tuple[Dict]: 包含音频数据和采样率的字典
        """
        # 检查是否为有效路径
        if not audio_video:
            raise ValueError("请选择有效的音频或视频文件")
        
        # 处理上传文件路径
        if audio_video.startswith("upload:"):
            # 从上传路径中提取文件名
            file_name = audio_video[7:]
            # 获取上传文件的完整路径
            file_path = folder_paths.get_annotated_filepath(file_name)
        else:
            # 直接使用提供的路径
            file_path = audio_video
        
        # 检查文件是否存在
        if not os.path.isfile(file_path):
            raise ValueError(f"文件不存在: {file_path}")
        
        # 检查文件扩展名
        ext = os.path.splitext(file_path)[1].lower()[1:]
        if ext not in self.ALLOWED_EXTENSIONS:
            raise ValueError(f"不支持的文件格式: {ext}，支持的格式: {', '.join(self.ALLOWED_EXTENSIONS)}")
        
        # 转换采样率为整数
        sr = int(sample_rate)
        
        # 加载音频
        audio_data, actual_sr = AudioVideoProcessor.load_audio(file_path, sr)
        
        # 创建音频对象
        audio_obj = {
            'data': audio_data,
            'sample_rate': actual_sr,
            'file_path': file_path,
            'file_name': os.path.basename(file_path)
        }
        
        return (audio_obj,)