# conftest.py
import pytest
from api.hospital_api import HospitalAPI


@pytest.fixture(scope="session")
def api_client():
    """整个测试会话只登录一次，拿到 Token 并返回带有 Token 的 API 客户端"""
    temp_api = HospitalAPI()
    login_res = temp_api.login()

    # 断言登录成功
    assert login_res["code"] == 200, "登录失败"

    # 提取你截图里存入环境的 api_token
    token = login_res["data"]["token"]
    print(
        f"\n========================================\n【Python拿到的Token】:\n{token}\n========================================\n")

    # 返回实例化好带 Token 的 API 客户端
    return HospitalAPI(token=token)