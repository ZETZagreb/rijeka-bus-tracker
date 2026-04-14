import os
import requests
from flask import Flask, render_template, jsonify

app = Flask(__name__)

def get_bus_type(gbr):
    try:
        num = int(gbr)
        # Plinski autobusi (CNG) u Rijeci
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
    # Izvor koji koristi busri.alwaysdata.net
    url = "https://cloud.it-sistemi.com/AutotrolejS3/api/v1/vehicle-positions"
    try:
        r = requests.get(url, timeout=10)
        data = r.json()
        vehicles = data.get("data", [])
        output = []
        for bus in vehicles:
            gbr = str(bus.get("vehicleNumber", ""))
            lat = bus.get("latitude")
            lon = bus.get("longitude")
            
            if not gbr or not lat: continue
            
            output.append({
                "garageNumber": gbr,
                "name": str(bus.get("lineName", "N/A")),
                "latitude": lat,
                "longitude": lon,
                "registration": bus.get("licensePlate", "N/A"),
                "destination": bus.get("destinationName", "N/A"),
                "type": get_bus_type(gbr),
                "speed": bus.get("speed", 0)
            })
        return jsonify({"vehicles": output})
    except:
        return jsonify({"vehicles": []})

@app.route('/api/stops/rijeka')
def get_rijeka_stops():
    # Izvor za stanice
    url = "https://cloud.it-sistemi.com/AutotrolejS3/api/v1/stops"
    try:
        r = requests.get(url, timeout=10)
        return jsonify(r.json().get("data", []))
    except:
        return jsonify([])

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
