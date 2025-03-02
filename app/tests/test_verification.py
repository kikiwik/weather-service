import unittest
from unittest.mock import AsyncMock, patch
import json
import time
from utils.services import create_verification_code  # 替换为实际模块路径

class TestCreateVerificationCode(unittest.IsolatedAsyncioTestCase):

    async def test_generate_verification_code(self):
        """测试能否生成6位数字验证码"""
        # 模拟 Redis 客户端
        redis_mock = AsyncMock()
        email = "user@example.com"
        
        # 调用待测试函数
        code = await create_verification_code(email, redis_mock)
        
        print(f"\n生成的验证码:{code}(类型{type(code)},(长度{len(code)}))")
        # 断言验证码格式正确
        self.assertEqual(len(code), 6, "验证码长度应为6位")
        self.assertTrue(code.isdigit(), "验证码应为纯数字")
    @patch('time.time')
    async def test_store_verification_code_to_redis(self, mock_time):
        """测试验证码是否正确存储到Redis"""
        # 固定当前时间戳
        mock_time.return_value = 1000.0
        
        # 模拟 Redis 客户端并记录行为
        redis_mock = AsyncMock()
        email = "user@example.com"
        
        # 调用待测试函数
        code = await create_verification_code(email, redis_mock)
        print(f"user{email}")
        # 断言 Redis set 方法被调用一次
        redis_mock.set.assert_awaited_once()
        
        # 提取调用参数
        call_args = redis_mock.set.await_args
        kwargs = call_args.kwargs
        
        # 验证 Redis 键名和过期时间
        self.assertEqual(kwargs['name'], email, "Redis键名应为邮箱地址")
        self.assertEqual(kwargs['ex'], 300, "Redis键过期时间应为300秒")
        stored_data = json.loads(kwargs['value'])
        self.assertEqual(stored_data['code'], code, "存储的验证码不一致")
        self.assertEqual(stored_data['timestamp'], 1000.0, "时间戳不正确")
        self.assertEqual(stored_data['expiry'], 1300.0, "过期时间应为当前时间+300秒")

if __name__ == '__main__':
    unittest.main()