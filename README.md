# 天气预警服务 

## 项目简介
一个基于FastAPI的天气查询微服务，提供多种天气查询方式，并集成AI智能分析。

## 功能特点
- 通过经纬度查询24小时天气预报
- 通过城市名称查询7天天气预报
- 支持用户注册、登录
- 权限控制机制
- **新增：AI天气智能分析**

## AI功能亮点
- 通过OpenAI API提供天气智能分析
- 实时生成personalized天气建议
- 提供详细的穿衣指南和活动建议
- 分析温度变化和天气风险

## 技术栈
- FastAPI
- SQLAlchemy (异步)
- Redis
- PostgreSQL
- 和风天气API
- **OpenAI API**

## 环境依赖
- Python 3.9+
- Poetry/Pip
- PostgreSQL
- Redis
- OpenAI API Key

## 安装步骤
1. 克隆仓库
```bash
git clone https://github.com/yourusername/weather-service.git
```

2. 安装依赖
```bash
pip install -r requirements.txt
pip install openai
```

3. 配置环境变量
- 复制 `.env.example` 到 `.env`
- 填写数据库、Redis和和风天气API配置
- **添加OpenAI API Key**

## 运行服务
```bash
uvicorn app.main:app --reload
```

## AI天气分析接口
### 请求示例
```bash
curl -X POST /weather-service/servers/get_weather_by_grid_with_ai_analysis \
     -H "Content-Type: application/json" \
     -d '{"lon": 116.41, "lat": 39.92}'
```

## 接口文档
服务启动后，访问 `/docs` 查看Swagger文档

## AI功能说明
- AI分析基于GPT-3.5-turbo
- 分析不影响主要天气数据返回
- 提供个性化、智能的天气建议

## 注意事项
- AI功能依赖OpenAI API
- 注意API调用频率和费用
- 建议添加缓存机制

## 许可证
MIT License

## 未来规划
- 支持多种AI模型
- 优化AI分析性能
- 增加更多个性化功能
