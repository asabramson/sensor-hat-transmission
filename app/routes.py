from flask import Blueprint, request, jsonify, render_template
from app.models import SensorData
from app import db

from sqlalchemy import func, and_
from datetime import datetime

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


# NON-API ROUTES

@main_bp.route('/', methods=['GET'])
@main_bp.route('/index', methods=['GET'])
def index():  
    return render_template('sensor.html') # using Jinja template loader to future-proof