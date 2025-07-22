from flask import Blueprint, request, jsonify, render_template
from app.models import SensorData
from app import db

from sqlalchemy import func, and_
from datetime import datetime, timedelta
import math, random

main_bp = Blueprint('app', __name__)
api_bp = Blueprint('api', __name__, url_prefix='/api')

@api_bp.route('/sensordata', methods=['POST'])
def ingest_sensor_data():
    """
    Expected JSON payload:
      {
        "d": 1, # device id, integer
        "t":  18.2, # temperature, float
        "h": 12.44, # humidity, float
        "p": 1010.73 # pressure, float
      }
    """
    payload = request.get_json(force=True)
    sample = SensorData(
      device_id = payload['d'],
      temperature = payload['t'],
      humidity = payload['h'],
      pressure = payload['p'],
      timestamp = datetime.now()
    )
    db.session.add(sample)
    db.session.commit()
    return jsonify({"status":"ok"}), 201




@api_bp.route('/sensordata/stats', methods=['GET'])
def get_stats():
    # find the max timestamp per device
    latest_ts = (
        db.session.query(
            SensorData.device_id,
            func.max(SensorData.timestamp).label('ts')
        )
        .group_by(SensorData.device_id)
        .subquery()
    )

    # join back to get full rows
    latest_samples = (
        db.session.query(SensorData)
        .join(
            latest_ts,
            and_(
                SensorData.device_id == latest_ts.c.device_id,
                SensorData.timestamp == latest_ts.c.ts
            )
        )
        .all()
    )

    # serialize into JSON
    data = [
        {
            "device_id":  s.device_id,
            "temperature": s.temperature,
            "humidity":    s.humidity,
            "pressure":    s.pressure,
            "timestamp":   s.timestamp.isoformat() + "Z"
        }
        for s in latest_samples
    ]
    return jsonify(data)

@api_bp.route('/sensordata/graphs', methods=['GET'])
def sensor_series():
    metric = request.args.get('metric')      # temperature, humidity, pressure
    period = request.args.get('period')      # hour, day, month

    field_map = {
      'temperature': SensorData.temperature,
      'humidity':    SensorData.humidity,
      'pressure':    SensorData.pressure
    }
    # ensure recieved request contains data in valid format
    if metric not in field_map or period not in ('hour','day','month'):
        return ("Bad request", 400)

    now = datetime.now()
    if period == 'hour':   delta = timedelta(hours=1)
    if period == 'day':    delta = timedelta(days=1)
    if period == 'month':  delta = timedelta(days=30)

    rows = (
      SensorData.query
        .filter(SensorData.timestamp >= now - delta)
        .order_by(SensorData.timestamp)
        .all()
    )

    data = [
      {
        "t": r.timestamp.isoformat(),
        "v": getattr(r, metric)
      }
      for r in rows
    ]
    return jsonify(data)

# ------------------------------ TRAFFIC SECTION ------------------------------

NUM_LOCATIONS = 6
SIM_DURATION   = 90 * 60   # program will run for 90 minutes (converted into seconds)
INTERVAL       = 30
SIM_STEPS      = 180       # 90 * 2 ticks per minute

# average visitors per 30 seconds for each location (ESTIMATES!)
AVG_VISITS = [0.60, 0.50, 0.40, 0.30, 0.20, 0.15]

_start_time = datetime.now()
# each will be populated with 180 values representing the number of visitors counted in the past 30 seconds
_in_series  = []
_out_series = []

# AI GENERATED AND RECOMMENDED USING POISSON SAMPLING
def _sample_poisson(lam: float) -> int:
    L = math.exp(-lam)
    k = 0
    p = 1.0
    while p > L:
        k += 1
        p *= random.random()
    return k - 1

# populate lists once at runtime
for lam in AVG_VISITS:
    _in_series.append([_sample_poisson(lam) for _ in range(SIM_STEPS)])
    _out_series.append([_sample_poisson(lam) for _ in range(SIM_STEPS)])


@api_bp.route('/traffic/live', methods=['GET'])
def live_traffic():
    now = datetime.now()
    elapsed = (now - _start_time).total_seconds()
    idx = int(elapsed // INTERVAL)
    if idx < 0: idx = 0
    if idx >= SIM_STEPS: idx = SIM_STEPS - 1

    result = []
    for loc in range(NUM_LOCATIONS):
        inc = _in_series[loc][idx]
        outc = _out_series[loc][idx]
        tot_in  = sum(_in_series[loc][: idx + 1])
        tot_out = sum(_out_series[loc][: idx + 1])
        cnt = tot_in - tot_out

        if   cnt < 1:          cong = "No Crowding"
        elif cnt < 3:          cong = "Minimal Crowding"
        elif cnt < 6:          cong = "Moderate Crowding"
        else:                  cong = "Heavy Crowding"

        result.append({
            "location_id": loc + 1,
            "in_count":    inc,
            "out_count":   outc,
            "total_in":    tot_in,
            "total_out":   tot_out,
            "count":       cnt,
            "congestion":  cong
        })

    return jsonify(result)

# NON-API ROUTES

@main_bp.route('/', methods=['GET'])
@main_bp.route('/index', methods=['GET'])
def index():  
    return render_template('traffic.html') # using Jinja template loader to future-proof EDIT BACK LATER