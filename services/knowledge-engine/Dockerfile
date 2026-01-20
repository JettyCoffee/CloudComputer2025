FROM python:3.13-slim

# 设置工作目录
WORKDIR /app

# 使用阿里云镜像源加速
RUN sed -i 's|deb.debian.org|mirrors.aliyun.com|g' /etc/apt/sources.list.d/debian.sources

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 安装 uv 包管理器（使用国内镜像）
RUN pip install --no-cache-dir -i https://mirrors.aliyun.com/pypi/simple/ uv

# 复制依赖文件
COPY pyproject.toml ./

# 使用 uv 安装依赖到系统 Python（使用国内镜像）
RUN uv pip install --system --no-cache --index-url https://mirrors.aliyun.com/pypi/simple/ -r pyproject.toml

# 复制应用代码
COPY . .

# 创建数据目录
RUN mkdir -p /app/data/graphs /app/data/documents /app/lightrag_workdir

# 暴露端口
EXPOSE 8002

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8002/health || exit 1

# 启动命令
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8002"]