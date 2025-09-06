# 示例工作流

本目录包含了一些示例工作流，帮助您快速上手使用Comfyui_NZ_ASR。

## 基本转录工作流

`basic_transcription.json` - 使用Whisper模型将音频转换为文本的基本工作流。

1. 加载Whisper模型（WhisperModelLoader）
2. 加载音频文件（LoadAudioVideo）
3. 转录为文本（AudioVideoToText）

## 带时间戳的转录工作流

`timestamped_transcription.json` - 使用FunASR模型将音频转换为带时间戳的文本的工作流。

1. 加载FunASR模型（FunASRModelLoader）
2. 加载音频文件（LoadAudioVideo）
3. 转录为带时间戳的SRT格式文本（AudioVideoToTimestampedText）

## 使用方法

1. 在ComfyUI中点击"Load"按钮
2. 导航到`custom_nodes/Comfyui_NZ_ASR/example_workflow`目录
3. 选择要加载的工作流文件
4. 点击"Load"按钮加载工作流
5. 根据需要修改工作流中的参数
6. 点击"Queue Prompt"按钮运行工作流