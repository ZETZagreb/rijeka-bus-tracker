import os
import requests
from flask import Flask, render_template, jsonify

app = Flask(__name__)

# Funkcija za određivanje tipa goriva prema garažnom broju
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
    # Službeni API za pozicije vozila
    url = "https://api.autotrolej.hr/api/open/v1/vehicles"
    try:
        r = requests.get(url, timeout=10)
        data = r.json()
        output = []
        for bus in data:
            gbr = str(bus.get("vehicleId", ""))
            if not gbr or bus.get("latitude") == 0: continue
            
            output.append({
                "garageNumber": gbr,
                "name": str(bus.get("lineCode", "")),
                "latitude": bus.get("latitude"),
                "longitude": bus.get("longitude"),
                "registration": bus.get("licensePlate", "N/A"),
                "destination": bus.get("destination", "N/A"),
                "type": get_bus_type(gbr),
                "speed": bus.get("speed", 0)
            })
        return jsonify({"vehicles": output})
    except:
        return jsonify({"vehicles": []})

@app.route('/api/stops/rijeka')
def get_rijeka_stops():
    # Službeni API za stanice
    url = "https://api.autotrolej.hr/api/open/v1/stops"
    try:
        r = requests.get(url, timeout=10)
        return jsonify(r.json())
    except:
        return jsonify([])

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
