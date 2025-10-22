# 天气预警服务

## 项目简介
一个基于FastAPI的天气查询微服务，提供多种天气查询方式。

## 功能特点
- 通过经纬度查询24小时天气预报
- 通过城市名称查询7天天气预报
- 通过行政编号查询城市天气
- 实时空气质量查询
- 天气预警查询
- 支持用户注册、登录
- 权限控制机制

## todo
- 天气日报的邮箱订阅与递送功能
- 基于ai的天气分析与建议

## 技术栈
- FastAPI
- SQLAlchemy (异步)
- Redis
- PostgreSQL
- 和风天气API

## 环境依赖
- Python 3.9+
- Poetry/Pip
- PostgreSQL
- Redis

## 安装步骤
1. 克隆仓库
```bash
git clone https://github.com/yourusername/weather-service.git
```

2. 安装依赖
```bash
pip install -r requirements.txt
```

3. 配置环境变量
- 复制 `.env.example` 到 `.env`
- 填写数据库、Redis和和风天气API配置

## 运行服务
```bash
uvicorn app.main:app --reload
```

## 接口文档
服务启动后，访问 `/docs` 查看Swagger文档

## 许可证
MIT License
