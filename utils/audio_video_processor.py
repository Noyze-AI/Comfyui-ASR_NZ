import os
import numpy as np
import importlib.util
from typing import Tuple, Union, Optional
from .logger import Logger

# 检查soundfile依赖
sf_spec = importlib.util.find_spec("soundfile")
if sf_spec is None:
    logger = Logger("AudioVideoProcessor")
    logger.warning("soundfile未安装，音频处理功能将不可用")
    sf = None
else:
    import soundfile as sf

# 检查ffmpeg依赖
ffmpeg_spec = importlib.util.find_spec("ffmpeg")
if ffmpeg_spec is None:
    logger = Logger("AudioVideoProcessor")
    logger.warning("ffmpeg-python未安装，视频处理功能将不可用")
    ffmpeg = None
else:
    import ffmpeg

class AudioVideoProcessor:
    """
    音频视频处理工具类，用于加载和处理音频和视频文件
    """
    
    @staticmethod
    def load_audio(file_path: str, sample_rate: int = 16000) -> Tuple[np.ndarray, int]:
        """
        加载音频文件或从视频文件中提取音频
        
        Args:
            file_path: 音频或视频文件路径
            sample_rate: 目标采样率，默认16000Hz
            
        Returns:
            Tuple[np.ndarray, int]: 音频数据和采样率
        """
        # 检查文件是否存在
        if not os.path.isfile(file_path):
            raise FileNotFoundError(f"文件不存在: {file_path}")
        
        # 获取文件扩展名
        ext = os.path.splitext(file_path)[1].lower()
        
        # 音频文件直接加载
        if ext in [".wav", ".mp3", ".flac", ".ogg"]:
            if sf is None:
                raise RuntimeError("无法处理音频文件: soundfile未安装，请安装后重试")
                
            try:
                audio, sr = sf.read(file_path)
                # 如果是立体声，转换为单声道
                if len(audio.shape) > 1 and audio.shape[1] > 1:
                    audio = audio.mean(axis=1)
                # 重采样到目标采样率
                if sr != sample_rate:
                    # 这里简化处理，实际项目中可能需要更复杂的重采样方法
                    audio = AudioVideoProcessor._resample(audio, sr, sample_rate)
                return audio, sample_rate
            except Exception as e:
                raise RuntimeError(f"加载音频文件失败: {e}")
        
        # 视频文件，使用ffmpeg提取音频
        elif ext in [".mp4", ".avi", ".mov", ".mkv", ".webm"]:
            if ffmpeg is None:
                raise RuntimeError("无法处理视频文件: ffmpeg-python未安装，请安装后重试")
            
            try:
                # 使用ffmpeg提取音频并转换为指定采样率
                audio_array, _ = (
                    ffmpeg.input(file_path)
                    .output('-', format='f32le', acodec='pcm_f32le', ac=1, ar=sample_rate)
                    .run(capture_stdout=True, capture_stderr=True)
                )
                audio = np.frombuffer(audio_array, np.float32)
                return audio, sample_rate
            except Exception as e:
                raise RuntimeError(f"从视频提取音频失败: {e}")
        else:
            raise ValueError(f"不支持的文件格式: {ext}")
    
    @staticmethod
    def _resample(audio: np.ndarray, orig_sr: int, target_sr: int) -> np.ndarray:
        """
        简单的重采样实现
        
        Args:
            audio: 音频数据
            orig_sr: 原始采样率
            target_sr: 目标采样率
            
        Returns:
            np.ndarray: 重采样后的音频数据
        """
        # 这里使用简单的线性插值，实际项目中可能需要更高质量的重采样方法
        if orig_sr == target_sr:
            return audio
            
        # 计算重采样后的长度
        new_length = int(len(audio) * target_sr / orig_sr)
        # 创建新的时间轴
        old_times = np.arange(len(audio)) / orig_sr
        new_times = np.arange(new_length) / target_sr
        # 线性插值
        resampled = np.interp(new_times, old_times, audio)
        return resampled
    
    @staticmethod
    def save_audio(audio: np.ndarray, file_path: str, sample_rate: int = 16000) -> None:
        """
        保存音频到文件
        
        Args:
            audio: 音频数据
            file_path: 保存路径
            sample_rate: 采样率
        """
        if sf is None:
            raise RuntimeError("无法保存音频文件: soundfile未安装，请安装后重试")
            
        sf.write(file_path, audio, sample_rate)
    
    @staticmethod
    def format_timestamp(seconds: float, include_ms: bool = True) -> str:
        """
        将秒数格式化为时间戳字符串 (HH:MM:SS.mmm)
        
        Args:
            seconds: 秒数
            include_ms: 是否包含毫秒
            
        Returns:
            str: 格式化的时间戳
        """
        hours = int(seconds // 3600)
        seconds %= 3600
        minutes = int(seconds // 60)
        seconds %= 60
        
        if include_ms:
            return f"{hours:02d}:{minutes:02d}:{seconds:06.3f}"
        else:
            return f"{hours:02d}:{minutes:02d}:{int(seconds):02d}"