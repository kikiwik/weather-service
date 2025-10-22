from fastapi import APIRouter,Depends,Request,HTTPException,Security
import requests
from sqlalchemy.ext.asyncio import AsyncSession
from redis import Redis
import openai  
import os
from dotenv import load_dotenv
from dao.redis import redis_connect
from dao import crud, databases,schemas
from utils import services

router = APIRouter()
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

@router.post("/get_weather_by_grid",dependencies=[Security(services.check_user,scopes=['query'])],response_model=schemas.ApiResponse)
async def get_weather_by_location(
    location: schemas.Grid
):
    url = "https://devapi.qweather.com/v7/grid-weather/24h"#todo 改为.env
    try:
        token =  services.get_api_token()
        params={
            "location": f"{location.lon},{location.lat}"
        }
        header_req = {"Authorization": f"Bearer {token}"}
        response =requests.get(url,params=params,headers=header_req)
        
        if response.status_code == 200:
            data = response.json()
            if "hourly" in data:
                # 仅保留每个小时预报中的 fxTime、temp、icon 和 text 字段
                filtered_hourly = []
                for item in data["hourly"]:
                    filtered_item = {
                        "fxTime": item.get("fxTime"),
                        "temp": item.get("temp"),
                        "icon": item.get("icon"),
                        "text": item.get("text")
                    }
                    filtered_hourly.append(filtered_item)
                data["hourly"] = filtered_hourly
            return {"code": schemas.ErrorCodes.SUCCESS, "message": "成功", "data": data}
        else:
            # 当第三方接口响应状态码不为200时，抛出第三方接口响应错误
            raise schemas.BusinessException(
                schemas.ErrorCodes.THIRD_PARTY_API_ERROR, "获取天气数据失败"
            )
    except schemas.BusinessException as be:
            raise be
    except Exception as e:
        # 捕捉未知错误，返回服务器内部错误：4007
            raise schemas.BusinessException(
            schemas.ErrorCodes.SERVER_INTERNAL_ERROR, f"服务器内部错误，请稍后重试: {str(e)}"
            )

            
async def fetch_weather_data(city_id_request: schemas.CityIdRequest):
    # 使用最新的天气预报接口地址，这里以七天预报为例，实际可根据需求选择 /v7/weather/3d 或 /v7/weather/7d
    url = "https://devapi.qweather.com/v7/weather/7d"  
    try:
        # 获取 API token（这里假设 token 实际上是 API key）
        token = services.get_api_token()
        params = {
            "location": city_id_request.city_id,
        }
        header_req = {"Authorization": f"Bearer {token}"}
        response =requests.get(url,params=params,headers=header_req)
        if response.status_code == 200:
            data = response.json()

            filtered_daily = []
            for item in data.get("daily", []):
                 filtered_daily.append({
                    "fxDate": item.get("fxDate"),
                    "tempMax": item.get("tempMax"),
                    "tempMin": item.get("tempMin"),
                    "textDay": item.get("textDay"),
                    "textNight": item.get("textNight")
                 })
            data["daily"] = filtered_daily

            return {"code": schemas.ErrorCodes.SUCCESS, "message": "成功", "data": data}
        else:
            error_detail = response.text
            print(f"错误详情: {error_detail}")
            raise  schemas.BusinessException(
            schemas.ErrorCodes.THIRD_PARTY_API_ERROR, f"服务请求失败: {str(e)}"
            )
    except schemas.BusinessException as be:
        # 已知业务异常直接传递给客户端
        raise be
    except Exception as e:
        raise schemas.BusinessException(
            schemas.ErrorCodes.SERVER_INTERNAL_ERROR, "服务器内部错误，请稍后重试"
        )
@router.post(
    "/get_weather_by_city_name",
    dependencies=[Security(services.check_user, scopes=['query'])],
    response_model=schemas.ApiResponse
)

async def get_weather_by_city_name(city: schemas.CityNameRequest):
    # 调用 GeoAPI 获取 city_id
    geo_url = "https://geoapi.qweather.com/v2/city/lookup"
    token = services.get_api_token()
    params = {
        "location": city.city_name,  # 城市名称
    }
    header_req = {"Authorization": f"Bearer {token}"}
    try:
        response = requests.get(geo_url, params=params,headers=header_req)
        if response.status_code == 200:
            data = response.json()
            if data.get("code") == "200":  # GeoAPI 成功
                locations = data.get("location", [])
                if locations:
                    city_id = locations[0].get("id")  # 取第一个匹配的城市 ID
                    print(city_id)
                    city_id_request = schemas.CityIdRequest(city_id=city_id)
                    # 使用 city_id 请求天气数据
                    return await fetch_weather_data(city_id_request)
                else:
                     raise schemas.BusinessException(
            schemas.ErrorCodes.CITY_NOT_EXIST, f"城市未找到: {str(e)}"
        )
            else:
                 raise schemas.BusinessException(
            schemas.ErrorCodes.SERVER_INTERNAL_ERROR, f"城市名称错误: {str(e)}"
        )
        else:
             raise schemas.BusinessException(
            schemas.ErrorCodes.SERVER_INTERNAL_ERROR, f"GeoAPI请求失败: {str(e)}"
        )
    except schemas.BusinessException as be:
        # 已知业务异常直接传递给客户端
        raise be
    except Exception as e:
        raise schemas.BusinessException(
            schemas.ErrorCodes.SERVER_INTERNAL_ERROR, "服务器内部错误，请稍后重试"
        )
@router.post("/get_weather_by_district_code", dependencies=[Security(services.check_user,scopes=['query'])], response_model=schemas.ApiResponse)
async def get_weather_by_district_code(
    district_code: schemas.DistrictCodeRequest,
):
    """
    通过行政区域编码查询天气预报
    支持精确到县区级别的天气查询
    """
    url = "https://devapi.qweather.com/v7/weather/7d"
    try:
        token = services.get_api_token()
        params = {
            "location": district_code.district_code,
        }
        header_req = {"Authorization": f"Bearer {token}"}
        response = requests.get(url, params=params, headers=header_req)
        
        if response.status_code == 200:
            data = response.json()
            filtered_daily = []
            for item in data.get("daily", []):
                filtered_daily.append({
                    "fxDate": item.get("fxDate"),
                    "tempMax": item.get("tempMax"),
                    "tempMin": item.get("tempMin"),
                    "textDay": item.get("textDay"),
                    "textNight": item.get("textNight"),
                    "windDir": item.get("windDir"),
                    "windScale": item.get("windScale")
                })
            data["daily"] = filtered_daily

            return {"code": schemas.ErrorCodes.SUCCESS, "message": "成功", "data": data}
        else:
            raise schemas.BusinessException(
                schemas.ErrorCodes.THIRD_PARTY_API_ERROR, "获取天气数据失败"
            )
    except schemas.BusinessException as be:
        raise be
    except Exception as e:
        raise schemas.BusinessException(
            schemas.ErrorCodes.SERVER_INTERNAL_ERROR, f"服务器内部错误: {str(e)}"
        )

@router.post("/get_air_quality", dependencies=[Security(services.check_user,scopes=['query'])], response_model=schemas.ApiResponse)
async def get_air_quality(
    location: schemas.Grid,
):
    """
    获取指定坐标点的实时空气质量情况
    """
    url = "https://devapi.qweather.com/v7/air/now"
    try:
        token = services.get_api_token()
        params = {
            "location": f"{location.lon},{location.lat}"
        }
        header_req = {"Authorization": f"Bearer {token}"}
        response = requests.get(url, params=params, headers=header_req)
        
        if response.status_code == 200:
            data = response.json()
            air_quality_data = {
                "primary_pollutant": data.get("now", {}).get("primary"),
                "air_quality_index": data.get("now", {}).get("aqi"),
                "quality_level": data.get("now", {}).get("category"),
                "pm10": data.get("now", {}).get("pm10"),
                "pm2_5": data.get("now", {}).get("pm2p5")
            }

            return {"code": schemas.ErrorCodes.SUCCESS, "message": "空气质量查询成功", "data": air_quality_data}
        else:
            raise schemas.BusinessException(
                schemas.ErrorCodes.THIRD_PARTY_API_ERROR, "获取空气质量数据失败"
            )
    except schemas.BusinessException as be:
        raise be
    except Exception as e:
        raise schemas.BusinessException(
            schemas.ErrorCodes.SERVER_INTERNAL_ERROR, f"服务器内部错误: {str(e)}"
        )

@router.post("/get_weather_warning", dependencies=[Security(services.check_user,scopes=['query'])], response_model=schemas.ApiResponse)
async def get_weather_warning(
    location: schemas.Grid,
):
    """
    获取指定坐标点的实时灾害预警信息
    """
    url = "https://devapi.qweather.com/v7/warning/now"
    try:
        token = services.get_api_token()
        params = {
            "location": f"{location.lon},{location.lat}"
        }
        header_req = {"Authorization": f"Bearer {token}"}
        response = requests.get(url, params=params, headers=header_req)
        
        if response.status_code == 200:
            data = response.json()
            warnings = []
            for warning in data.get("warning", []):
                warnings.append({
                    "title": warning.get("title"),
                    "type": warning.get("type"),
                    "level": warning.get("level"),
                    "text": warning.get("text")
                })

            return {"code": schemas.ErrorCodes.SUCCESS, "message": "灾害预警查询成功", "data": warnings}
        else:
            raise schemas.BusinessException(
                schemas.ErrorCodes.THIRD_PARTY_API_ERROR, "获取灾害预警数据失败"
            )
    except schemas.BusinessException as be:
        raise be
    except Exception as e:
        raise schemas.BusinessException(
            schemas.ErrorCodes.SERVER_INTERNAL_ERROR, f"服务器内部错误: {str(e)}"
        )

@router.post("/get_weather_by_grid_with_ai_analysis", 
             dependencies=[Security(services.check_user,scopes=['query'])], 
             response_model=schemas.WeatherWithAIAnalysisResponse)
async def get_weather_by_location_with_ai_analysis(
    location: schemas.Grid
):
    """
    通过经纬度查询天气并进行AI智能分析
    """
    url = "https://devapi.qweather.com/v7/grid-weather/24h"
    try:
        token = services.get_api_token()
        params = {
            "location": f"{location.lon},{location.lat}"
        }
        header_req = {"Authorization": f"Bearer {token}"}
        response = requests.get(url, params=params, headers=header_req)
        
        if response.status_code == 200:
            data = response.json()
            
            # 过滤和处理天气数据
            if "hourly" in data:
                filtered_hourly = []
                for item in data["hourly"]:
                    filtered_item = {
                        "fxTime": item.get("fxTime"),
                        "temp": item.get("temp"),
                        "icon": item.get("icon"),
                        "text": item.get("text")
                    }
                    filtered_hourly.append(filtered_item)
                data["hourly"] = filtered_hourly
            
            # 准备AI分析的提示词
            ai_prompt = f"""
            根据以下24小时天气数据，给出详细的天气分析和生活建议：
            {json.dumps(data['hourly'], ensure_ascii=False)}
            
            请按照以下要求分析：
            1. 温度变化趋势
            2. 可能的天气变化
            3. 对日常生活的具体建议
            4. 需要注意的天气风险
            5. 穿衣指南
            6. 户外活动建议
            """
            
            # 调用OpenAI API进行分析
            try:
                ai_response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "你是一个专业的气象分析助手"},
                        {"role": "user", "content": ai_prompt}
                    ],
                    max_tokens=500
                )
                
                ai_analysis = ai_response.choices[0].message.content
                
                return {
                    "code": schemas.ErrorCodes.SUCCESS, 
                    "message": "成功", 
                    "data": {
                        "weather_data": data,
                        "ai_analysis": ai_analysis
                    }
                }
            
            except Exception as ai_error:
                # AI分析失败不影响主要天气数据返回
                return {
                    "code": schemas.ErrorCodes.SUCCESS, 
                    "message": "天气数据获取成功，但AI分析出现问题", 
                    "data": {
                        "weather_data": data,
                        "ai_analysis": "AI分析暂时不可用"
                    }
                }
        
        else:
            raise schemas.BusinessException(
                schemas.ErrorCodes.THIRD_PARTY_API_ERROR, "获取天气数据失败"
            )
    
    except schemas.BusinessException as be:
        raise be
    except Exception as e:
        raise schemas.BusinessException(
            schemas.ErrorCodes.SERVER_INTERNAL_ERROR, f"服务器内部错误: {str(e)}"
        )