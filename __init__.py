import os
import sys
import folder_paths

NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}

# 注册Web目录
WEB_DIRECTORY = os.path.join(os.path.dirname(os.path.realpath(__file__)), "web")

# 将Web目录添加到ComfyUI的Web扩展目录中
from pathlib import Path
if Path(WEB_DIRECTORY).exists():
    if "web_extensions_dirs" not in folder_paths.__dict__:
        folder_paths.web_extensions_dirs = []
    folder_paths.web_extensions_dirs.append(WEB_DIRECTORY)

# 导入节点模块
from .nodes.funasr_loader import FunASRModelLoader
from .nodes.whisper_loader import WhisperModelLoader
from .nodes.audio_video_loader import LoadAudioVideo
from .nodes.audio_to_text import AudioVideoToText
from .nodes.audio_to_timestamped_text import AudioVideoToTimestampedText

# 注册节点
NODE_CLASS_MAPPINGS["FunASRModelLoader"] = FunASRModelLoader
NODE_CLASS_MAPPINGS["WhisperModelLoader"] = WhisperModelLoader
NODE_CLASS_MAPPINGS["LoadAudioVideo"] = LoadAudioVideo
NODE_CLASS_MAPPINGS["AudioVideoToText"] = AudioVideoToText
NODE_CLASS_MAPPINGS["AudioVideoToTimestampedText"] = AudioVideoToTimestampedText

# 设置节点显示名称
NODE_DISPLAY_NAME_MAPPINGS["FunASRModelLoader"] = "加载FunASR模型"
NODE_DISPLAY_NAME_MAPPINGS["WhisperModelLoader"] = "加载Whisper模型"
NODE_DISPLAY_NAME_MAPPINGS["LoadAudioVideo"] = "加载音频/视频"
NODE_DISPLAY_NAME_MAPPINGS["AudioVideoToText"] = "音频转文本"
NODE_DISPLAY_NAME_MAPPINGS["AudioVideoToTimestampedText"] = "音频转带时间戳文本"

# 设置模型路径
ASR_MODELS_DIR = os.path.join(folder_paths.models_dir, "ASR")
FUNASR_MODELS_DIR = os.path.join(ASR_MODELS_DIR, "FunASR")
WHISPER_MODELS_DIR = os.path.join(ASR_MODELS_DIR, "Whisper")

# 创建模型目录
os.makedirs(FUNASR_MODELS_DIR, exist_ok=True)
os.makedirs(WHISPER_MODELS_DIR, exist_ok=True)

# 添加模型路径到ComfyUI的模型路径中
folder_paths.add_model_folder_path("FunASR", FUNASR_MODELS_DIR)
folder_paths.add_model_folder_path("Whisper", WHISPER_MODELS_DIR)

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']