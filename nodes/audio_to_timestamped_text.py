import os
from typing import Dict, List, Tuple, Union, Optional

from ..engines.funasr_engine import FunASREngine
from ..utils.audio_video_processor import AudioVideoProcessor

class AudioVideoToTimestampedText:
    """
    音频转带时间戳文本节点
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "audio": ("AUDIO",),
                "format": (["srt", "vtt", "txt", "json"], {
                    "default": "srt"
                }),
            },
            "optional": {
                "funasr_model": ("FUNASR_MODEL",),
                "whisper_model": ("WHISPER_MODEL",),
            }
        }
    
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("timestamped_text",)
    FUNCTION = "transcribe_with_timestamps"
    CATEGORY = "NOYZE"
    
    def transcribe_with_timestamps(self, audio: Dict, format: str, funasr_model: Optional[FunASREngine] = None, whisper_model: Optional[Dict] = None) -> Tuple[str]:
        """
        将音频转换为带时间戳的文本
        
        Args:
            audio: 音频对象
            format: 输出格式，可选值包括srt, vtt, txt, json
            funasr_model: FunASR模型对象
            whisper_model: Whisper模型对象
            
        Returns:
            Tuple[str]: 带时间戳的文本
        """
        if funasr_model is None and whisper_model is None:
            raise ValueError("请至少提供一个ASR模型（FunASR或Whisper）")
        
        # 获取音频数据
        audio_data = audio['data']
        sample_rate = audio['sample_rate']
        
        # 获取带时间戳的转录结果
        segments = []
        
        # 优先使用Whisper模型（如果提供）
        if whisper_model is not None:
            engine = whisper_model['engine']
            params = whisper_model['params']
            
            # 调用Whisper引擎进行转录
            segments = engine.transcribe_with_timestamps(audio_data, **params)
        
        # 使用FunASR模型
        elif funasr_model is not None:
            # 调用FunASR引擎进行转录
            segments = funasr_model.transcribe_with_timestamps(audio_data)
        
        # 根据指定格式输出结果
        if format == "json":
            # 直接返回JSON格式的字符串
            import json
            return (json.dumps(segments, ensure_ascii=False, indent=2),)
        
        elif format == "srt":
            # 转换为SRT格式
            srt_text = self._to_srt(segments)
            return (srt_text,)
        
        elif format == "vtt":
            # 转换为VTT格式
            vtt_text = self._to_vtt(segments)
            return (vtt_text,)
        
        else:  # txt
            # 转换为纯文本格式，带时间戳
            txt_text = self._to_txt(segments)
            return (txt_text,)
    
    def _to_srt(self, segments: List[Dict]) -> str:
        """
        将分段转换为SRT格式
        
        Args:
            segments: 分段列表
            
        Returns:
            str: SRT格式的字符串
        """
        srt_lines = []
        
        for i, segment in enumerate(segments):
            # 获取开始和结束时间
            start_time = segment['start']
            end_time = segment['end']
            text = segment['text']
            
            # 格式化时间戳 (HH:MM:SS,mmm)
            start_formatted = self._format_time_srt(start_time)
            end_formatted = self._format_time_srt(end_time)
            
            # 添加SRT条目
            srt_lines.append(f"{i+1}")
            srt_lines.append(f"{start_formatted} --> {end_formatted}")
            srt_lines.append(f"{text.strip()}")
            srt_lines.append("")
        
        return "\n".join(srt_lines)
    
    def _to_vtt(self, segments: List[Dict]) -> str:
        """
        将分段转换为VTT格式
        
        Args:
            segments: 分段列表
            
        Returns:
            str: VTT格式的字符串
        """
        vtt_lines = ["WEBVTT", ""]
        
        for i, segment in enumerate(segments):
            # 获取开始和结束时间
            start_time = segment['start']
            end_time = segment['end']
            text = segment['text']
            
            # 格式化时间戳 (HH:MM:SS.mmm)
            start_formatted = self._format_time_vtt(start_time)
            end_formatted = self._format_time_vtt(end_time)
            
            # 添加VTT条目
            vtt_lines.append(f"{start_formatted} --> {end_formatted}")
            vtt_lines.append(f"{text.strip()}")
            vtt_lines.append("")
        
        return "\n".join(vtt_lines)
    
    def _to_txt(self, segments: List[Dict]) -> str:
        """
        将分段转换为带时间戳的纯文本格式
        
        Args:
            segments: 分段列表
            
        Returns:
            str: 带时间戳的纯文本
        """
        txt_lines = []
        
        for segment in segments:
            # 获取开始和结束时间
            start_time = segment['start']
            end_time = segment['end']
            text = segment['text']
            
            # 格式化时间戳 (HH:MM:SS)
            start_formatted = AudioVideoProcessor.format_timestamp(start_time, include_ms=False)
            end_formatted = AudioVideoProcessor.format_timestamp(end_time, include_ms=False)
            
            # 添加文本条目
            txt_lines.append(f"[{start_formatted} --> {end_formatted}] {text.strip()}")
        
        return "\n".join(txt_lines)
    
    def _format_time_srt(self, seconds: float) -> str:
        """
        将秒数格式化为SRT时间戳格式 (HH:MM:SS,mmm)
        
        Args:
            seconds: 秒数
            
        Returns:
            str: 格式化的SRT时间戳
        """
        hours = int(seconds // 3600)
        seconds %= 3600
        minutes = int(seconds // 60)
        seconds %= 60
        milliseconds = int((seconds - int(seconds)) * 1000)
        
        return f"{hours:02d}:{minutes:02d}:{int(seconds):02d},{milliseconds:03d}"
    
    def _format_time_vtt(self, seconds: float) -> str:
        """
        将秒数格式化为VTT时间戳格式 (HH:MM:SS.mmm)
        
        Args:
            seconds: 秒数
            
        Returns:
            str: 格式化的VTT时间戳
        """
        hours = int(seconds // 3600)
        seconds %= 3600
        minutes = int(seconds // 60)
        seconds %= 60
        milliseconds = int((seconds - int(seconds)) * 1000)
        
        return f"{hours:02d}:{minutes:02d}:{int(seconds):02d}.{milliseconds:03d}"