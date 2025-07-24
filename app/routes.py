from flask import Blueprint, request, jsonify, render_template, url_for
from app.models import SensorData, TrafficData
from app import db
from app.traffic_csv_parser import get_day_hours, get_month_totals

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
# ordered by: BBHL, Jordan, Otter, Schoodic, SDM, Seawall
AVG_VISITS = [0.30, 0.70, 0.55, 0.30, 0.25, 0.15]

_start_time = datetime.now()
# each will be populated with 180 values representing the number of visitors counted in the past 30 seconds
_in_series  = []
_out_series = []

# AI RECOMMENDED USING POISSON SAMPLING AND GENERATED THE FOLLOWING SNIPPET
def _sample_poisson(lam: float) -> int:
    L = math.exp(-lam)
    k = 0
    p = 1.0
    while p > L:
        k += 1
        p *= random.random()
    return k - 1

# populate lists once at runtime independently of API/route calls
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

        if   cnt < 2:          cong = "No Crowding"
        elif cnt < 5:          cong = "Minimal Crowding"
        elif cnt < 7:          cong = "Moderate Crowding"
        else:                  cong = "Heavy Crowding"

        # Real world implementation would populate and query database instead of global variables
        # Global variables were used here for simplicity and for easier testing
        #
        # sample = TrafficData(
        #     location_id = loc + 1,
        #     in_count = inc,
        #     out_count = outc,
        #     timestamp = datetime.now()
        # )
        #
        # db.session.add(sample)
        # db.session.commit()

        loc+=1
        # Virtual environment used for testing used Python 3.9, match statements are only in 3.10 and later
        if loc == 1:
            loc_str = "BHHL"
        elif loc == 2:
            loc_str = "Jordan Pond"
        elif loc == 3:
            loc_str = "Otter Cliff"
        elif loc == 4:
            loc_str = "Schoodic"
        elif loc == 5:
            loc_str = "Sieur de Monts"
        else:
            loc_str = "Seawall"

        result.append({
            "location_id": loc_str,
            "in_count":    inc,
            "out_count":   outc,
            "total_in":    tot_in,
            "total_out":   tot_out,
            "count":       cnt,
            "congestion":  cong
        })

    return jsonify(result)



@api_bp.route('/traffic/day_series')
def traffic_day_series():
    loc = int(request.args.get('loc', 1))
    day = int(request.args.get('day', 26))

    # Virtual environment used for testing used Python 3.9, match statements are only in 3.10 and later
    if loc == 1:
        loc_str = "bhhl"
    elif loc == 2:
        loc_str = "jordan"
    elif loc == 3:
        loc_str = "otter"
    elif loc == 4:
        loc_str = "schoodic"
    elif loc == 5:
        loc_str = "sdm"
    else:
        loc_str = "seawall"

    in_hours, out_hours = get_day_hours(loc_str, day)
    return jsonify({
        "hours": list(range(1,25)),
        "inbound": in_hours,
        "outbound": out_hours
    })

@api_bp.route('/traffic/month_series')
def traffic_month_series():
    loc = int(request.args.get('loc', 1))

    # Virtual environment used for testing used Python 3.9, match statements are only in 3.10 and later
    if loc == 1:
        loc_str = "bhhl"
    elif loc == 2:
        loc_str = "jordan"
    elif loc == 3:
        loc_str = "otter"
    elif loc == 4:
        loc_str = "schoodic"
    elif loc == 5:
        loc_str = "sdm"
    else:
        loc_str = "seawall"

    days, in_tot, out_tot = get_month_totals(loc_str)
    return jsonify({
        "days": days,
        "inbound": in_tot,
        "outbound": out_tot
    })


# NON-API ROUTES

@main_bp.route('/', methods=['GET'])
@main_bp.route('/index', methods=['GET'])
def index():  
    return render_template('traffic.html') # using Jinja template loader instead of load_static to future-proof

@main_bp.route('/sensordata', methods=['GET'])
def sensor_route():  
    return render_template('sensor.html') # using Jinja template loader instead of load_static to future-proof