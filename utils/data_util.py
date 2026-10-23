from faker import Faker
import random

fake = Faker('zh_CN')

def generate_patient_info():
    """生成挂号需要的随机患者信息"""
    return{
        "name":f"测试患者_{random.randint(1000,9999)}",
        "id_card":fake.ssn(),
        "phone":fake.phone_number(),
        "mock_id_card":f"11010519900520{random.randint(1000,9999)}"
    }

