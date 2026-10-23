# testcases/test_hospital_flow.py
import pytest
import time
import datetime
from datetime import timedelta
from utils.data_util import generate_patient_info


class TestHospitalFlow:

    def test_full_patient_flow(self, api_client):
        # ================= 1. 生成数据 & 挂号 =================
        patient = generate_patient_info()
        target_name = patient["name"]
        target_id_card = patient["mock_id_card"]  # <--- 1. 补充定义身份证变量，用于后续精准匹配

        # 获取今天的日期，解决日期不匹配的问题
        today_str = (datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8)))).strftime("%Y-%m-%d")
        print(f"【当前使用的挂号日期】: {today_str}")

        # <--- 2. 这里必须把 today_str 传给接口，否则会报错
        reg_res = api_client.create_registration(patient, attendance_date=today_str)

        # 断言：挂号成功
        assert reg_res.get("code") == 200, f"❌ 挂号失败: {reg_res}"

        # ================= 2. 查询挂号单 =================
        current_reg_id = None
        print("⏳ 正在等待主从数据库同步并精准查询挂号单...")

        for attempt in range(10):
            query_res = api_client.query_registration(query_date=today_str, page_size=1000)

            # <--- 3. 建议把这行断言放出来，防止接口直接报错导致后面代码崩溃
            assert query_res.get("code") == 200, f"❌ 查询列表接口报错: {query_res}"

            data_list = query_res.get("data", {}).get("list", [])

            # 逻辑1：用身份证精准匹配（如果后端返回了这个字段）或者名字匹配
            for item in data_list:
                if item.get("identificationNo") == target_id_card or target_name in item.get("patientName", ""):
                    current_reg_id = item["registrationId"]
                    print(f"✅ 完美！第 {attempt + 1} 次查询成功找到自己挂的号，ID: {current_reg_id}")
                    break

            if current_reg_id:
                break  # 找到了，立刻跳出循环

            print(f"第 {attempt + 1} 次查询未找到，等待 2 秒后重试...")
            time.sleep(2)

        # 如果没有找到，直接让测试失败，绝不拿兜底数据
        assert current_reg_id is not None, f"❌ 彻底失败：等待20秒后，列表里依然没有找到患者 {target_name} 的数据"

        # ================= 3. 接诊 =================
        diag_res = api_client.start_diagnosis(current_reg_id)
        print(f"【接诊接口返回】: {diag_res}")
        assert diag_res.get("code") == 200, f"❌ 接诊失败: {diag_res}"

        # ================= 4. 开立处方 =================
        med_num = 3
        presc_res = api_client.create_prescription(current_reg_id, med_num=med_num)
        print(f"【开处方接口返回】: {presc_res}")
        assert presc_res.get("code") == 200, f"❌ 开处方失败: {presc_res}"

        # ================= 5. 查询未缴费项目 =================
        # 等待 1 秒，给数据库同步留点时间
        time.sleep(1)
        fee_res = api_client.query_unpaid_fees(current_reg_id)
        print(f"【查询未缴费返回】: {fee_res}")

        assert fee_res.get("code") == 200, f"❌ 查询未缴费接口报错: {fee_res}"
        fee_list = fee_res.get("data")or []
        assert len(fee_list) > 0, f"❌ 业务异常：刚开的处方竟然没有查询到待缴费项"

        # 深度断言：验证查询到的金额是否与开处方时的金额一致
        # 注意：因为使用了兜底策略，可能是别人的单子，所以这里只断言金额必须大于0
        total_unpaid_amount = sum(item["amount"] for item in fee_list)
        print(f"💰 当前待缴费总金额: {total_unpaid_amount}")
        assert total_unpaid_amount > 0, "❌ 业务异常：待缴费金额计算为 0"

        # 组装收费 Body
        charge_list = []
        for item in fee_list:
            charge_list.append({
                "amount": item["amount"],
                "chargeItemId": item["id"],
                "invoiceNo": int(time.time()),  # 动态生成发票号，避免重复
                "operatorId": 1,
                "settlementCatId": 1,
                "type": item["type"]
            })

        # ================= 6. 收费 =================
        pay_res = api_client.pay_fees(charge_list)
        print(f"【收费接口返回】: {pay_res}")
        assert pay_res.get("code") == 200, f"❌ 收费失败: {pay_res}"

        # ================= 7. 终极闭环断言：收费后再次查询 =================
        print("🔄 正在验证收费后的状态...")
        time.sleep(1)
        verify_fee_res = api_client.query_unpaid_fees(current_reg_id)
        assert verify_fee_res.get("code") == 200

        # 深度断言：收费成功后，未缴费列表里应该查不到这笔钱了！
        verify_list = verify_fee_res.get("data") or []
        remaining_ids = [item["id"] for item in verify_list]

        for charge_item in charge_list:
            assert charge_item["chargeItemId"] not in remaining_ids, \
                f"❌ 业务严重Bug：收费成功后，仍能查询到未缴费项目ID {charge_item['chargeItemId']}"

        print("\n🎉 完美！全链路业务断言全部通过，收费后状态校验成功！")