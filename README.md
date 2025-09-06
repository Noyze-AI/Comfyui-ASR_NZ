# Comfyui_NZ_ASR - ComfyUI音视频转文本节点

这个项目为ComfyUI提供了音视频转文本的功能，支持使用FunASR和Whisper两种ASR引擎进行语音识别。

## 功能特点

- 支持多种音频和视频格式的加载
- 支持FunASR和Whisper两种ASR引擎
- 支持多种语言的语音识别
- 支持输出带时间戳的文本，格式包括SRT、VTT、TXT和JSON
- 自动下载和管理ASR模型

## 安装方法

1. 将本项目克隆到ComfyUI的`custom_nodes`目录下：

```bash
cd ComfyUI/custom_nodes
git clone https://github.com/yourusername/Comfyui_NZ_ASR.git
```

2. 安装依赖：

```bash
cd Comfyui_NZ_ASR
pip install -r requirements.txt
```

3. 重启ComfyUI

## 使用方法

### 基本工作流

1. 使用`FunASRModelLoader`或`WhisperModelLoader`节点加载ASR模型
2. 使用`LoadAudioVideo`节点加载音频或视频文件
3. 使用`AudioVideoToText`或`AudioVideoToTimestampedText`节点进行转录

### 节点说明

#### FunASRModelLoader

加载FunASR模型。

- 输入：
  - `model_id`：模型ID，可选值包括`paraformer-zh`、`paraformer-zh-vad`、`paraformer-en`、`paraformer-en-vad`
- 输出：
  - `funasr_model`：FunASR模型对象

#### WhisperModelLoader

加载Whisper模型。

- 输入：
  - `model_id`：模型ID，可选值包括`tiny`、`tiny.en`、`base`、`base.en`、`small`、`small.en`、`medium`、`medium.en`、`large`、`large-v2`、`large-v3`
  - `language`：语言代码，如`zh`、`en`等，空字符串表示自动检测
  - `task`：任务类型，`transcribe`或`translate`
- 输出：
  - `whisper_model`：Whisper模型对象

#### LoadAudioVideo

加载音频或视频文件。

- 输入：
  - `audio_video`：音频或视频文件
  - `sample_rate`：采样率，可选值包括`16000`、`22050`、`44100`、`48000`
- 输出：
  - `audio`：音频对象

#### AudioVideoToText

将音频转换为文本。

- 输入：
  - `audio`：音频对象
  - `funasr_model`（可选）：FunASR模型对象
  - `whisper_model`（可选）：Whisper模型对象
- 输出：
  - `text`：转录的文本

#### AudioVideoToTimestampedText

将音频转换为带时间戳的文本。

- 输入：
  - `audio`：音频对象
  - `format`：输出格式，可选值包括`srt`、`vtt`、`txt`、`json`
  - `funasr_model`（可选）：FunASR模型对象
  - `whisper_model`（可选）：Whisper模型对象
- 输出：
  - `timestamped_text`：带时间戳的文本

## 模型说明

### FunASR模型

FunASR模型将自动下载到`ComfyUI/models/ASR/FunASR`目录下。

可用的FunASR模型：

- `paraformer-zh`：Paraformer中文语音识别模型
- `paraformer-zh-vad`：Paraformer中文语音识别模型（带VAD和标点）
- `paraformer-en`：Paraformer英文语音识别模型
- `paraformer-en-vad`：Paraformer英文语音识别模型（带VAD和标点）

### Whisper模型

Whisper模型将自动下载到`ComfyUI/models/ASR/Whisper`目录下。

可用的Whisper模型：

- `tiny`：Tiny模型 (39M参数)
- `tiny.en`：Tiny模型 - 英文优化 (39M参数)
- `base`：Base模型 (74M参数)
- `base.en`：Base模型 - 英文优化 (74M参数)
- `small`：Small模型 (244M参数)
- `small.en`：Small模型 - 英文优化 (244M参数)
- `medium`：Medium模型 (769M参数)
- `medium.en`：Medium模型 - 英文优化 (769M参数)
- `large`：Large模型 (1550M参数)
- `large-v2`：Large-v2模型 (1550M参数)
- `large-v3`：Large-v3模型 (1550M参数)

## 示例工作流

### 基本转录工作流

1. 加载Whisper模型（WhisperModelLoader）
2. 加载音频文件（LoadAudioVideo）
3. 转录为文本（AudioVideoToText）

### 带时间戳的转录工作流

1. 加载FunASR模型（FunASRModelLoader）
2. 加载视频文件（LoadAudioVideo）
3. 转录为带时间戳的SRT格式文本（AudioVideoToTimestampedText）

## 许可证

[MIT License](LICENSE)