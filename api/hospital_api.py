# api/hospital_api.py
import requests
import json
import time
from config import BASE_URL


class HospitalAPI:
    def __init__(self, token=None):
        self.base_url = BASE_URL
        self.token = token
        # 统一加上伪装浏览器的 UA，防止被网关拦截
        self.headers = {
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "*/*",
            "Connection": "keep-alive"
        }
        if token:
            self.headers["Authorization"] = f"Bearer {token}"

    def login(self, username="admin", password="admin123456"):
        url = f"{self.base_url}/staff/login"
        payload = {"username": username, "password": password}
        # 登录不需要 token，但也带上伪装 UA
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        return requests.post(url, json=payload, headers=headers).json()

    def create_registration(self, patient_data, attendance_date):
        url = f"{self.base_url}/registration/createRegistration"

        payload = {
            "amount": 15,
            "attendanceDate": attendance_date,  # <--- 这里用参数，千万别写死！
            "dateOfBirth": "2000-10-19",
            "deptId": 3,
            "gender": 1,
            "homeAddress": "北京市朝阳区某某街道1号",
            "identificationNo": patient_data["mock_id_card"],
            "invoiceNo": int(time.time()),  # 动态发票号
            "name": patient_data["name"],
            "needBook": 0,
            "operatorId": 1,
            "phoneNo": patient_data["phone"],
            "settlementCatId": 1,
            "skdId": None
        }

        import json
        return requests.post(url, data=json.dumps(payload), headers=self.headers).json()

    # 下面这些先不改，等挂号跑通了再说
    def query_registration(self, query_date="2026-10-19", page_num=1, page_size=1000):
        url = f"{self.base_url}/fee/listRegisteredPatient"
        params = {"queryDate": query_date, "pageNum": page_num, "pageSize": page_size}
        return requests.get(url, params=params, headers=self.headers).json()

    def start_diagnosis(self, reg_id):
        url = f"{self.base_url}/diagnosisPatient/startDiagnosis"
        params = {"registrationId": reg_id}
        return requests.get(url, params=params, headers=self.headers).json()

    def create_prescription(self, reg_id, med_num=3):
        url = f"{self.base_url}/DmsMedicinePrescriptionRecord/apply"
        price = 1.07
        payload = {
            "amount": round(med_num * price, 2), "name": "门诊西药处方",
            "registrationId": reg_id, "status": 1, "type": 1, "createStaffId": 1,
            "dmsMedicineItemRecordList": [{
                "drugId": 12, "num": med_num, "price": price,
                "medicineUsage": 1, "frequency": 1, "days": 3, "medicalAdvice": "遵医嘱按时服用"
            }]
        }
        return requests.post(url, json=payload, headers=self.headers).json()

    def query_unpaid_fees(self, reg_id):
        url = f"{self.base_url}/fee/listChargeByRegistrationId"
        params = {"registrationId": reg_id}
        return requests.get(url, params=params, headers=self.headers).json()

    def pay_fees(self, charge_body):
        url = f"{self.base_url}/fee/charge"
        return requests.post(url, json=charge_body, headers=self.headers).json()