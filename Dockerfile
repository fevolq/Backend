# 基础镜像
FROM python:3.7-slim-buster

# 设置工作目录
WORKDIR /app

# 复制代码到容器中
COPY . /app

# 程序默认端口
EXPOSE 1123

# 安装依赖
RUN pip install --no-cache-dir -r requirements.txt

# 启动命令
CMD ["python", "main.py"]
