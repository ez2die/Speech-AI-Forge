#!/bin/bash

# macOS Apple Silicon 安装脚本
# Speech-AI-Forge macOS Apple Silicon Installation Script

echo "🍦 Speech-AI-Forge macOS Apple Silicon 安装脚本"
echo "================================================"

# 检查是否为Apple Silicon Mac
if [[ $(uname -m) != "arm64" ]]; then
    echo "⚠️  警告: 此脚本专为Apple Silicon Mac设计"
    echo "    如果您使用Intel Mac，请使用标准的requirements.txt"
fi

# 检查Python版本
python_version=$(python3 --version 2>&1 | awk '{print $2}' | cut -d. -f1-2)
required_version="3.8"

if [[ $(echo "$python_version $required_version" | awk '{print ($1 >= $2)}') -eq 0 ]]; then
    echo "❌ Python版本过低: $python_version (需要 >= $required_version)"
    echo "   请升级Python版本"
    exit 1
fi

echo "✅ Python版本检查通过: $python_version"

# 检查是否已安装Homebrew
if ! command -v brew &> /dev/null; then
    echo "❌ 未找到Homebrew，请先安装："
    echo "   /bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
    exit 1
fi

echo "✅ Homebrew已安装"

# 安装系统依赖
echo "📦 安装系统依赖..."
brew install ffmpeg portaudio

# 创建虚拟环境（如果不存在）
if [ ! -d ".venv" ]; then
    echo "🔧 创建Python虚拟环境..."
    python3 -m venv .venv
fi

# 激活虚拟环境
echo "🔧 激活虚拟环境..."
source .venv/bin/activate

# 升级pip
echo "⬆️  升级pip..."
pip install --upgrade pip

# 安装依赖
echo "📦 安装Python依赖..."
pip install -r requirements.macos.txt

echo ""
echo "🎉 安装完成！"
echo ""
echo "📋 使用说明:"
echo "   1. 激活虚拟环境: source .venv/bin/activate"
echo "   2. 下载模型: python -m scripts.download_models --source modelscope"
echo "   3. 启动WebUI: python webui.py"
echo "   4. 启动API服务: python launch.py"
echo ""
echo "📖 更多信息请查看README.md"
echo ""
echo "⚡ Apple Silicon优化:"
echo "   - 使用MPS加速 (Metal Performance Shaders)"
echo "   - 针对ARM64架构优化的PyTorch"
echo "   - 移除了CUDA相关依赖" 