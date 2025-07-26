import requests
import datetime
import random
import time

building_id = "building_001"
url = "http://localhost:8000/data"

# Generate energy data for past 3 days at 30-minute intervals
now = datetime.datetime.utcnow()

for day_offset in range(3, 0, -1):
    for hour in range(0, 24):
        for minute in [0, 30]:
            timestamp = now - datetime.timedelta(days=day_offset, hours=(23-hour), minutes=(60-minute))
            payload = {
                "building_id": building_id,
                "timestamp": timestamp.isoformat(),
                "electricity_kWh": round(random.uniform(100, 350), 2),
                "water_liters": round(random.uniform(100, 400), 2),
                "temperature_c": round(random.uniform(20, 28), 1)
            }
            response = requests.post(url, json=payload)
            print(f"Sent: {payload['timestamp']} | Status: {response.status_code}")
            time.sleep(0.05)
