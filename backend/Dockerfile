# 1. 使用官方 Python 3.13 基础镜像
FROM python:3.13-slim-bookworm

# 2. 从官方镜像获取 uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# 3. 设置工作目录
WORKDIR /app

# 4. 设置环境变量 
ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy 
ENV PATH="/app/.venv/bin:$PATH"

# 5. 安装系统依赖
# 6. 复制依赖定义文件 
COPY pyproject.toml uv.lock* ./

# 7. 安装依赖
# --frozen: 严格按照 uv.lock 安装 
RUN uv sync --frozen --no-install-project --no-dev || uv sync --no-install-project --no-dev

# 8. 复制源代码
COPY . .

# 9. 暴露端口
EXPOSE 8000

# 10. 启动命令
# 使用虚拟环境中的 uvicorn 启动 Central Agent
CMD ["uvicorn", "central_agent.main:app", "--host", "0.0.0.0", "--port", "8000"]