import requests
import json

# 1. 填入你刚才打印出来的 Token
token = "eyJhbGciOiJIUzUxMiJ9.eyJzdWIiOiJhZG1pbiIsImNyZWF0ZWQiOjE3OTI2NjQwNzQwMjIsImV4cCI6MTc5MzI2ODg3NH0.Q5uIB7RLUe7rRKiWy9SVim0ut7-0NbQJOrh6kFZpX3f2MDztFNNWvBZ4yikgUwqGPzW_PpnLGCdxSKGeerHL-g"
url = "http://101.43.51.98:10099/registration/createRegistration"

# 2. 完美复刻浏览器的所有 Headers（关键点：伪装 User-Agent）
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {token}",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "*/*",
    "Connection": "keep-alive"
}

# 3. 完全照抄你图2里 Web 抓包的 Payload
payload = {
    "amount": 15,
    "attendanceDate": "2026-10-19",
    "dateOfBirth": "2010-02-25",
    "deptId": 3,
    "gender": 0,
    "homeAddress": "22222222222222222",
    "identificationNo": "123432343333",
    "invoiceNo": 63357075,
    "name": "11111111",
    "needBook": 0,
    "operatorId": 1,      # 必须带
    "phoneNo": "1233333333",
    "settlementCatId": 1,
    "skdId": None         # 必须带
}

# 4. 发送请求
print("正在发送请求...")
# 使用 data=json.dumps(payload) 完全模拟 Postman 的生成代码
response = requests.post(url, headers=headers, data=json.dumps(payload))

print(f"状态码: {response.status_code}")
print(f"服务器返回: {response.text}")