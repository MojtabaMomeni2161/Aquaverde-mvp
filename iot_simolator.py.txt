import requests
import random
import time
from datetime import datetime

API_URL = "http://localhost:5000/api/iot/data"
FARM_ID = 1  # این را به آیدی مزرعه خود در دیتابیس تغییر دهید
SENSOR_ID = "SIM_SENSOR_001"

def send_water_data():
    flow_rate = random.uniform(1.0, 4.5)
    pressure = random.uniform(1.2, 2.8)
    
    data = {
        "sensor_id": SENSOR_ID,
        "water_flow": round(flow_rate, 2),
        "pressure": round(pressure, 2),
        "farm_id": FARM_ID,
        "timestamp": datetime.now().isoformat()
    }
    
    try:
        response = requests.post(API_URL, json=data, timeout=5)
        if response.status_code == 200:
            print(f"✅ [{datetime.now().strftime('%H:%M:%S')}] ارسال: {flow_rate:.2f} L/s | فشار: {pressure:.1f} bar")
        else:
            print(f"❌ خطا: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ خطا: {e}")

if __name__ == "__main__":
    print("🚀 شبیه‌ساز سنسور آکواورد")
    print("📍 آدرس سرور:", API_URL)
    print("⏱️ ارسال هر ۱۰ ثانیه... (Ctrl+C برای توقف)")
    while True:
        send_water_data()
        time.sleep(10)