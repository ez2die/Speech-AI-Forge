# 🍦 Speech-AI-Forge for macOS Apple Silicon

这是 Speech-AI-Forge 针对 macOS Apple Silicon (M1/M2/M3/M4) 芯片的优化版本。

## 🚀 快速开始

### 系统要求

- macOS 12.0+ (Monterey或更高版本)
- Apple Silicon 芯片 (M1/M2/M3/M4)
- Python 3.8+
- Homebrew
- 至少8GB RAM (推荐16GB+)

### 一键安装

```bash
# 克隆仓库
git clone https://github.com/ez2die/Speech-AI-Forge.git
cd Speech-AI-Forge

# 运行macOS安装脚本
./install_macos.sh
```

### 手动安装

如果您偏好手动安装：

```bash
# 1. 安装系统依赖
brew install ffmpeg portaudio

# 2. 创建虚拟环境
python3 -m venv .venv
source .venv/bin/activate

# 3. 安装Python依赖
pip install -r requirements.macos.txt

# 4. 下载模型
python -m scripts.download_models --source modelscope
```

## 🎯 Apple Silicon 优化特性

### 硬件加速
- **MPS (Metal Performance Shaders)**: 利用Apple的GPU加速
- **ARM64优化**: 针对Apple Silicon架构优化的PyTorch
- **内存管理**: 优化的内存使用和垃圾回收

### 兼容性改进
- 移除CUDA依赖，避免兼容性问题
- 针对macOS的音频处理优化
- 支持Apple的AVFoundation框架

## 🔧 使用说明

### 启动WebUI
```bash
source .venv/bin/activate
python webui.py
```

### 启动API服务
```bash
source .venv/bin/activate
python launch.py
```

## 🎵 支持的模型

所有主要模型都已针对Apple Silicon优化：

| 模型类别        | 模型名称         | Apple Silicon支持 | MPS加速 |
| --------------- | --------------- | ----------------- | ------- |
| **TTS**         | ChatTTS         | ✅                | ✅      |
|                 | FishSpeech      | ✅                | ✅      |
|                 | CosyVoice       | ✅                | ✅      |
|                 | FireRedTTS      | ✅                | ✅      |
|                 | F5-TTS          | ✅                | ✅      |
|                 | GPT-SoVITS      | ✅                | ✅      |
| **ASR**         | Whisper         | ✅                | ✅      |
|                 | SenseVoice      | ✅                | ✅      |
| **Enhancer**    | ResembleEnhance | ✅                | ✅      |

## 🐛 常见问题

### 性能优化

1. **启用MPS加速**：
   ```python
   # 系统会自动检测并使用MPS
   # 如需强制使用CPU: export USE_CPU=all
   ```

2. **内存不足**：
   ```bash
   # 关闭其他应用程序
   # 使用较小的batch size
   # 考虑升级到16GB+内存
   ```

### 安装问题

1. **权限问题**：
   ```bash
   sudo chown -R $(whoami) /opt/homebrew
   ```

2. **Python版本**：
   ```bash
   # 使用pyenv管理Python版本
   brew install pyenv
   pyenv install 3.11.7
   pyenv global 3.11.7
   ```

3. **FFmpeg问题**：
   ```bash
   brew reinstall ffmpeg
   ```

## 🔧 环境变量

```bash
# 强制使用CPU (禁用MPS)
export USE_CPU=all

# 设置设备ID (通常不需要)
export DEVICE_ID=0

# 禁用半精度 (如遇到问题)
export NO_HALF=true
```

## 📊 性能基准

在M2 Pro (16GB RAM) 上的测试结果：

| 任务           | 处理时间  | 内存使用 |
| -------------- | --------- | -------- |
| ChatTTS (短文本) | ~2-3秒   | ~4GB     |
| Whisper ASR    | ~实时1.5x | ~2GB     |
| 音频增强       | ~5秒/分钟 | ~3GB     |

## 🛠️ 开发指南

### 调试模式
```bash
export PYTORCH_ENABLE_MPS_FALLBACK=1
export PYTORCH_MPS_HIGH_WATERMARK_RATIO=0.0
python webui.py --debug
```

### 性能分析
```bash
# 启用MPS性能分析
export PYTORCH_MPS_LOG_FILENAME=mps_log.txt
```

## 🤝 贡献

欢迎为macOS Apple Silicon适配贡献代码：

1. Fork 这个仓库
2. 创建feature分支
3. 提交您的更改
4. 创建Pull Request

## 📄 许可证

本项目采用 AGPL-3.0 许可证。

## 🔗 相关链接

- [原始项目](https://github.com/lenML/Speech-AI-Forge)
- [Apple Silicon优化指南](https://developer.apple.com/documentation/metalperformanceshaders)
- [PyTorch MPS文档](https://pytorch.org/docs/stable/notes/mps.html)

---

**享受在Apple Silicon上的高性能语音AI体验！** 🎉 