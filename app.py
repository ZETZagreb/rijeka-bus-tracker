import os
import requests
from flask import Flask, render_template, jsonify
from datetime import datetime, timedelta

app = Flask(__name__)

def get_bus_type(gbr):
    try:
        num = int(gbr)
        if 716 <= num <= 725 or 731 <= num <= 750 or 811 <= num <= 830:
            return "cng"
    except:
        pass
    return "diesel"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/buses/rijeka')
def get_rijeka_buses():
    url = "https://cloud.it-sistemi.com/AutotrolejS3/api/v1/vehicle-positions"
    try:
        r = requests.get(url, timeout=10)
        data = r.json()
        vehicles = data.get("data", [])
        output = []
        for bus in vehicles:
            gbr = str(bus.get("vehicleNumber", ""))
            line = str(bus.get("lineName", ""))
            lat = bus.get("latitude")
            lon = bus.get("longitude")
            reg = bus.get("licensePlate", "N/A")
            dest = bus.get("destinationName", "N/A")
            if not gbr or not lat: continue
            output.append({
                "garageNumber": gbr,
                "name": line,
                "latitude": lat,
                "longitude": lon,
                "registration": reg,
                "destination": dest,
                "type": get_bus_type(gbr),
                "speed": bus.get("speed", 0)
            })
        return jsonify({"vehicles": output})
    except:
        return jsonify({"vehicles": []})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
