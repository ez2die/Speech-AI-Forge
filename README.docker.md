# 🐳 Speech-AI-Forge Docker 部署指南

这是 Speech-AI-Forge 的完整 Docker 部署解决方案，支持 CPU 和 GPU 两种模式，适用于开发、测试和生产环境。

## 🚀 快速开始

### 一键部署

```bash
# 克隆仓库
git clone https://github.com/ez2die/Speech-AI-Forge.git
cd Speech-AI-Forge

# 一键部署 (CPU模式)
./docker-deploy.sh up

# 一键部署 (GPU模式)
./docker-deploy.sh up-gpu
```

部署完成后访问：
- **WebUI**: http://localhost:7860
- **API**: http://localhost:7870
- **API文档**: http://localhost:7870/docs

## 📋 系统要求

### 基础要求
- Docker 20.10+
- Docker Compose 2.0+
- 8GB+ RAM
- 20GB+ 可用磁盘空间

### GPU模式额外要求
- NVIDIA GPU (支持CUDA 11.8+)
- NVIDIA Docker Runtime
- NVIDIA GPU Driver 470+

## 🛠️ 安装步骤

### 1. 安装 Docker

#### Ubuntu/Debian
```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
```

#### macOS
```bash
# 使用 Homebrew
brew install --cask docker
```

### 2. 安装 NVIDIA Docker (GPU模式)

```bash
# 添加NVIDIA包仓库
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | sudo tee /etc/apt/sources.list.d/nvidia-docker.list

# 安装NVIDIA Docker
sudo apt-get update && sudo apt-get install -y nvidia-docker2
sudo systemctl restart docker
```

## 🎯 部署模式

### CPU 模式 (推荐用于开发)

```bash
# 构建和启动
./docker-deploy.sh up
```

### GPU 模式 (推荐用于生产)

```bash
# 构建和启动
./docker-deploy.sh up-gpu
```

## 🔧 配置管理

### 环境变量

复制并修改环境配置：
```bash
cp env.example .env
nano .env
```

主要配置选项：

| 变量名 | 默认值 | 说明 |
|--------|--------|------|
| `COMPUTE_TYPE` | `cpu` | 计算类型: cpu/gpu |
| `USE_CPU` | - | 强制CPU模式 |
| `API_PORT` | `7870` | API服务端口 |
| `WEBUI_PORT` | `7860` | WebUI端口 |

## 🎨 管理命令

### 使用部署脚本

```bash
# 查看帮助
./docker-deploy.sh --help

# 构建镜像
./docker-deploy.sh build

# 启动服务
./docker-deploy.sh up          # CPU模式
./docker-deploy.sh up-gpu      # GPU模式

# 查看状态
./docker-deploy.sh status

# 查看日志
./docker-deploy.sh logs

# 停止服务
./docker-deploy.sh down
```

## 📊 监控和调试

### 查看资源使用

```bash
# 容器状态
docker-compose ps

# 资源使用情况
docker stats
```

### 日志管理

```bash
# 查看所有服务日志
docker-compose logs

# 实时跟踪日志
docker-compose logs -f --tail=100
```

## 🐛 故障排除

### 常见问题

1. **端口冲突**
   ```bash
   # 检查端口占用
   lsof -i :7860
   lsof -i :7870
   ```

2. **内存不足**
   ```bash
   # 监控内存使用
   docker stats
   ```

3. **GPU不可用**
   ```bash
   # 检查NVIDIA驱动
   nvidia-smi
   ```

## 📚 相关资源

- [Docker官方文档](https://docs.docker.com/)
- [原项目仓库](https://github.com/lenML/Speech-AI-Forge)

---

**享受容器化的Speech-AI-Forge体验！** 🎉 