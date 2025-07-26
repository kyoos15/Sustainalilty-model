from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional
import datetime
import random
from collections import defaultdict

app = FastAPI()

energy_data_store = []

class EnergyData(BaseModel):
    building_id: str
    timestamp: datetime.datetime
    electricity_kWh: float
    water_liters: Optional[float] = None
    temperature_c: Optional[float] = None

@app.post("/data")
def ingest_data(entry: EnergyData):
    energy_data_store.append(entry.dict())
    return {"status": "success", "entry": entry}

@app.get("/data/{building_id}")
def get_data(building_id: str):
    results = [e for e in energy_data_store if e['building_id'] == building_id]
    return {"data": results}

@app.get("/suggestions/{building_id}")
def get_suggestions(building_id: str):
    tips = [
        "Turn off idle equipment.",
        "Use natural light.",
        "Maintain HVAC.",
        "Optimize AC settings.",
        "Schedule tasks in off-peak times."
    ]
    return {"tips": random.sample(tips, 3)}

@app.get("/alerts/{building_id}")
def generate_alerts(building_id: str):
    alerts = []
    for e in energy_data_store:
        if e['building_id'] == building_id and e['electricity_kWh'] > 300:
            alerts.append({"timestamp": e['timestamp'], "alert": "High electricity usage detected!"})
    return {"alerts": alerts}

@app.get("/weekly_report/{building_id}")
def weekly_report(building_id: str):
    now = datetime.datetime.utcnow()
    last_week = now - datetime.timedelta(days=7)
    data = [e for e in energy_data_store if e['building_id'] == building_id and datetime.datetime.fromisoformat(str(e['timestamp'])) > last_week]

    if not data:
        return {"message": "No data found for the last 7 days."}

    total_energy = sum(e['electricity_kWh'] for e in data)
    avg_energy = total_energy / len(data)
    score = max(0, 100 - int(avg_energy / 5))

    return {
        "building_id": building_id,
        "entries": len(data),
        "total_energy_kWh": round(total_energy, 2),
        "average_energy_kWh": round(avg_energy, 2),
        "sustainability_score": score
    }

@app.get("/gamification/{building_id}")
def gamified_progress(building_id: str):
    streak = 0
    today = datetime.datetime.utcnow().date()
    energy_by_day = defaultdict(float)

    for e in energy_data_store:
        if e['building_id'] == building_id:
            day = datetime.datetime.fromisoformat(str(e['timestamp'])).date()
            energy_by_day[day] += e['electricity_kWh']

    for i in range(7):
        check_day = today - datetime.timedelta(days=i)
        if energy_by_day[check_day] <= 250:
            streak += 1
        else:
            break

    return {"building_id": building_id, "energy_saving_streak_days": streak, "threshold_kWh": 250}

@app.get("/predict_energy/{building_id}")
def predict_energy(building_id: str):
    pred = round(random.uniform(200, 350), 2)
    return {"building_id": building_id, "predicted_next_usage_kWh": pred, "note": "Stub prediction"}

@app.get("/leaderboard")
def leaderboard():
    now = datetime.datetime.utcnow()
    last_week = now - datetime.timedelta(days=7)
    building_energy = defaultdict(float)
    building_counts = defaultdict(int)

    for e in energy_data_store:
        ts = datetime.datetime.fromisoformat(str(e['timestamp']))
        if ts > last_week:
            building_energy[e['building_id']] += e['electricity_kWh']
            building_counts[e['building_id']] += 1

    scores = []
    for bid in building_energy:
        avg = building_energy[bid] / building_counts[bid]
        score = max(0, 100 - int(avg / 5))
        scores.append((bid, score))

    sorted_scores = sorted(scores, key=lambda x: x[1], reverse=True)
    return {"leaderboard": [{"building_id": bid, "score": sc} for bid, sc in sorted_scores]}

@app.post("/simulate/{building_id}")
def simulate_energy_data(building_id: str):
    now = datetime.datetime.utcnow()
    for i in range(48):
        timestamp = now - datetime.timedelta(minutes=i * 30)
        electricity = round(random.uniform(100, 350), 2)
        entry = EnergyData(building_id=building_id, timestamp=timestamp, electricity_kWh=electricity)
        energy_data_store.append(entry.dict())
    return {"status": "simulation_complete", "entries_added": 48}
