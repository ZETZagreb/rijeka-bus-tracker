import os
import requests
from flask import Flask, render_template, jsonify
from google.transit import gtfs_realtime_pb2

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/buses/rijeka')
def get_rijeka_buses():
    # Službeni link s portala grada Rijeke
    url = "https://servisi.rijeka.hr/gtfs/vehicle_positions.pb"
    try:
        response = requests.get(url, timeout=10)
        feed = gtfs_realtime_pb2.FeedMessage()
        feed.ParseFromString(response.content)
        
        output = []
        for entity in feed.entity:
            if entity.HasField('vehicle'):
                # Izvlačimo podatke: gbr, liniju, lat, lon
                output.append({
                    "garageNumber": entity.vehicle.vehicle.id,
                    "name": entity.vehicle.trip.route_id, # Broj linije
                    "latitude": entity.vehicle.position.latitude,
                    "longitude": entity.vehicle.position.longitude,
                    "speed": round(entity.vehicle.position.speed or 0, 1)
                })
        return jsonify({"vehicles": output})
    except Exception as e:
        print(f"Greška: {e}")
        return jsonify({"vehicles": [], "error": str(e)})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
