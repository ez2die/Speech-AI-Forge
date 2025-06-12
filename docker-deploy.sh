#!/bin/bash

# Speech-AI-Forge Docker Deployment Script
# 🐳 Docker 部署脚本

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

# 帮助信息
show_help() {
    cat << EOF
🍦 Speech-AI-Forge Docker 部署脚本

使用方法:
  ./docker-deploy.sh [选项] [命令]

命令:
  build       构建Docker镜像
  up          启动服务 (默认CPU模式)
  up-gpu      启动服务 (GPU模式)
  down        停止服务
  logs        查看日志
  status      查看服务状态
  clean       清理所有容器和镜像
  update      更新并重新部署

选项:
  -h, --help     显示帮助信息
  -v, --verbose  详细输出
  --no-cache     构建时不使用缓存
  --force        强制执行操作

示例:
  ./docker-deploy.sh build          # 构建镜像
  ./docker-deploy.sh up             # 启动CPU模式
  ./docker-deploy.sh up-gpu         # 启动GPU模式
  ./docker-deploy.sh logs           # 查看日志
  ./docker-deploy.sh down           # 停止服务

EOF
}

# 检查系统要求
check_requirements() {
    log "检查系统要求..."
    
    # 检查Docker
    if ! command -v docker &> /dev/null; then
        error "Docker 未安装。请先安装 Docker: https://docs.docker.com/get-docker/"
        exit 1
    fi
    
    # 检查Docker Compose
    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        error "Docker Compose 未安装。请先安装 Docker Compose"
        exit 1
    fi
    
    # 检查Docker是否运行
    if ! docker info &> /dev/null; then
        error "Docker daemon 未运行。请启动 Docker 服务"
        exit 1
    fi
    
    log "✅ 系统要求检查通过"
}

# 检查GPU支持
check_gpu_support() {
    if command -v nvidia-smi &> /dev/null; then
        log "✅ 检测到 NVIDIA GPU"
        nvidia-smi --query-gpu=name,memory.total --format=csv,noheader,nounits
        return 0
    else
        warn "⚠️  未检测到 NVIDIA GPU 或驱动"
        return 1
    fi
}

# 创建必要目录
create_directories() {
    log "创建必要目录..."
    mkdir -p data/speakers models logs
    log "✅ 目录创建完成"
}

# 创建环境文件
create_env_file() {
    if [ ! -f ".env" ]; then
        log "创建环境配置文件..."
        cp env.example .env
        log "✅ 已创建 .env 文件，请根据需要修改配置"
    else
        log "环境配置文件已存在"
    fi
}

# 构建镜像
build_images() {
    log "构建 Docker 镜像..."
    
    local build_args=""
    if [ "$NO_CACHE" = "true" ]; then
        build_args="--no-cache"
    fi
    
    # 构建CPU版本
    log "构建 CPU 版本..."
    docker build $build_args --build-arg COMPUTE_TYPE=cpu -t speech-ai-forge:cpu .
    
    # 如果有GPU，构建GPU版本
    if check_gpu_support; then
        log "构建 GPU 版本..."
        docker build $build_args --build-arg COMPUTE_TYPE=gpu -t speech-ai-forge:gpu .
    fi
    
    log "✅ 镜像构建完成"
}

# 启动服务 (CPU模式)
start_cpu() {
    log "启动 Speech-AI-Forge (CPU 模式)..."
    docker-compose up -d speech-ai-forge-api speech-ai-forge-webui
    
    log "等待服务启动..."
    sleep 10
    
    show_service_info
}

# 启动服务 (GPU模式)
start_gpu() {
    if ! check_gpu_support; then
        error "GPU 模式需要 NVIDIA GPU 支持"
        exit 1
    fi
    
    log "启动 Speech-AI-Forge (GPU 模式)..."
    docker-compose --profile gpu up -d
    
    log "等待服务启动..."
    sleep 10
    
    show_service_info
}

# 停止服务
stop_services() {
    log "停止 Speech-AI-Forge 服务..."
    docker-compose down
    log "✅ 服务已停止"
}

# 查看日志
show_logs() {
    log "显示服务日志..."
    docker-compose logs -f
}

# 查看服务状态
show_status() {
    log "服务状态:"
    docker-compose ps
    echo
    
    log "容器资源使用情况:"
    docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.MemPerc}}"
}

# 显示服务信息
show_service_info() {
    echo
    info "🎉 Speech-AI-Forge 部署完成!"
    echo
    info "服务访问地址:"
    info "  📱 WebUI:  http://localhost:7860"
    info "  🔌 API:    http://localhost:7870"
    info "  📚 API文档: http://localhost:7870/docs"
    echo
    info "常用命令:"
    info "  查看日志: ./docker-deploy.sh logs"
    info "  查看状态: ./docker-deploy.sh status"
    info "  停止服务: ./docker-deploy.sh down"
    echo
}

# 清理资源
clean_all() {
    warn "⚠️  这将删除所有 Speech-AI-Forge 相关的容器和镜像"
    read -p "确认继续? (y/N): " -n 1 -r
    echo
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        log "清理容器..."
        docker-compose down -v --remove-orphans
        
        log "清理镜像..."
        docker rmi -f speech-ai-forge:cpu speech-ai-forge:gpu 2>/dev/null || true
        
        log "清理未使用的资源..."
        docker system prune -f
        
        log "✅ 清理完成"
    else
        log "操作已取消"
    fi
}

# 更新并重新部署
update_deployment() {
    log "更新 Speech-AI-Forge..."
    
    # 停止服务
    stop_services
    
    # 更新代码 (如果是git仓库)
    if [ -d ".git" ]; then
        log "更新代码..."
        git pull
    fi
    
    # 重新构建
    build_images
    
    # 重新启动
    if check_gpu_support; then
        warn "检测到GPU，将启动GPU模式"
        start_gpu
    else
        start_cpu
    fi
}

# 参数解析
VERBOSE=false
NO_CACHE=false
FORCE=false

while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_help
            exit 0
            ;;
        -v|--verbose)
            VERBOSE=true
            shift
            ;;
        --no-cache)
            NO_CACHE=true
            shift
            ;;
        --force)
            FORCE=true
            shift
            ;;
        build|up|up-gpu|down|logs|status|clean|update)
            COMMAND=$1
            shift
            ;;
        *)
            error "未知参数: $1"
            show_help
            exit 1
            ;;
    esac
done

# 如果没有指定命令，显示帮助
if [ -z "$COMMAND" ]; then
    show_help
    exit 0
fi

# 设置详细输出
if [ "$VERBOSE" = "true" ]; then
    set -x
fi

# 主要逻辑
log "🍦 Speech-AI-Forge Docker 部署脚本"
log "================================================"

# 检查系统要求
check_requirements

# 创建必要文件和目录
create_directories
create_env_file

# 执行命令
case $COMMAND in
    build)
        build_images
        ;;
    up)
        build_images
        start_cpu
        ;;
    up-gpu)
        build_images
        start_gpu
        ;;
    down)
        stop_services
        ;;
    logs)
        show_logs
        ;;
    status)
        show_status
        ;;
    clean)
        clean_all
        ;;
    update)
        update_deployment
        ;;
    *)
        error "未知命令: $COMMAND"
        show_help
        exit 1
        ;;
esac

log "操作完成! 🎉" 