所有图像或者遮罩输入或者输出必须使用 BHWC 或者 BHW 形状的张量，需要文字输出时输出为字符串
CATEGORY = NOYZE
未指定文件夹时请在当前文件夹下创建__init__.py文件，并将节点代码添加到__init__.py文件中
初次创建时需要添加节点注册
编辑好代码后检査是否存在有没有使用的模块，不要导入没有必要或者没有使用的模块
需要的依赖在requirements.txt文件中列出





# ComfyUI 音视频转文本节点项目规划

## 项目整体架构

### 1. 文件结构

```
Comfyui_NZ_ASR/
├── __init__.py          # 主入口文件，包含节点注册
├── nodes/               # 节点定义目录
│   ├── __init__.py      # 节点导出
│   ├── funasr_loader.py # FunASR模型加载节点
│   ├── whisper_loader.py # Whisper模型加载节点
│   ├── audio_video_loader.py  # 音频视频加载节点
│   ├── audio_to_text.py # 音频转文本节点
│   └── audio_to_timestamped_text.py # 音频转带时间戳文本节点
├── engines/             # ASR引擎实现
│   ├── __init__.py      # 引擎接口定义
│   ├── funasr_engine.py # FunASR引擎实现
│   └── whisper_engine.py # Whisper引擎实现
├── utils/               # 工具函数
│   ├── __init__.py
│   ├── audio_video_processor.py    # 音视频处理
├── models/              # 模型管理
│   ├── __init__.py
│   ├── funasr_models.py # FunASR模型管理
│   └── whisper_models.py # Whisper模型管理
├── example_workflow/    # 示例工作流
├── requirements.txt     # 项目依赖
└── README.md           # 项目文档
```

### 2. 节点结构

1. **FunASRModelLoader** (nodes/funasr_loader.py)
   - 输入：FunASR模型类型(下拉菜单)，模型名称(下拉菜单)
   - 输出：FunASR模型对象

2. **WhisperModelLoader** (nodes/whisper_loader.py)
   - 输入：Whisper模型类型(下拉菜单)，模型名称(下拉菜单)
   - 输出：Whisper模型对象

3. **LoadAudioVideo** (nodes/audio_loader.py)
   - 输入：点击load按钮后弹出文件管理器选择音视频
   - 输出：音频对象

4. **AudioVideoToText** (nodes/audio_to_text.py)
   - 输入：音频对象，FunASR模型对象,Whisper模型对象
   - 输出：文本字符串

5. **AudioVideoToTimestampedText** (nodes/audio_to_timestamped_text.py)
   - 输入：音频对象，FunASR模型对象,Whisper模型对象
   - 输出：带时间戳的文本字符串

### 3. ASR引擎实现
参考这两个项目，分别理解他们的ASR引擎实现方式
https://github.com/avenstack/ComfyUI-AV-FunASR.git
https://github.com/yuvraj108c/ComfyUI-Whisper
然后分别在 `engines/funasr_engine.py` 和 `engines/whisper_engine.py` 中实现具体引擎。

### 4. 音频/视频处理流程

1. **LoadAudioVideo** 节点：
   - 用户选择音频/视频文件
   - 如果是视频，提取音频轨道
   - 根据需要进行音频预处理
   - 返回标准化的音频对象

2. **AudioVideoToText** / **AudioVideoToTimestampedText** 节点：
   - 接收音频对象和ASR模型对象
   - 调用相应ASR引擎的转录方法
   - 返回文本结果

### 5. 依赖管理

主要依赖项：

```
torch
numpy
ffmpeg-python  # 音视频处理
funasr         # FunASR引擎
openai-whisper # Whisper引擎
soundfile     # 音频文件处理
```

### 6. 模型管理

1. 模型存储路径：
   - FunASR模型：`models/ASR/FunASR/{model_name}`
   - Whisper模型：`models/ASR/Whisper/{model_name}`

2. 模型加载流程：
   - 检查本地是否存在模型
   - 如不存在，提示用户下载或自动下载
   - 加载模型到内存
   - 返回模型对象

## 节点注册

在 `__init__.py` 中注册所有节点：   