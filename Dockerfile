# 使用轻量级的 Python 3.11 基础镜像
FROM python:3.11-slim

# 将 uv 二进制文件直接复制到镜像中
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# 设置容器内的工作目录
WORKDIR /app

COPY pyproject.toml uv.lock ./

RUN uv pip install --system -r pyproject.toml 

COPY . .

CMD ["python", "main.py"]