# 1. 使用官方 Python 基础镜像
FROM python:3.12-slim

# 2. 设置环境变量
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# 3. 设置工作目录
WORKDIR /code/app

# 4. (新) 安装编译依赖项
# 我们安装 build-essential (包含 gcc) 和 libmysqlclient-dev (asyncmy 可能需要)
RUN apt-get update && apt-get install -y \
    build-essential \
    libmariadb-dev \
    libmariadb-dev-compat \
    --no-install-recommends && \
    rm -rf /var/lib/apt/lists/*

# 5. 复制并安装依赖
COPY app/requirements.txt /code/app/
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r /code/app/requirements.txt

# 6. 复制整个 app 目录
COPY app/ /code/app/

# 7. 暴露 uvicorn 运行的端口
EXPOSE 8000

# 8. 运行 uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]