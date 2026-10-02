import os
import requests
from flask import Flask, jsonify
from flask_cors import CORS
from google.transit import gtfs_realtime_pb2

app = Flask(__name__)
CORS(app)

ZET_PROTOBUF_URL = "https://www.zet.hr/gtfs-rt-protobuf"

@app.route('/')
def home():
    return jsonify({"status": "ok", "message": "ZET Live Backend je aktivan!"})

@app.route('/podaci')
def get_data():
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(ZET_PROTOBUF_URL, headers=headers, timeout=10)
        
        if response.status_code != 200:
            return jsonify({"error": f"ZET API vratio status {response.status_code}"}), 500

        feed = gtfs_realtime_pb2.FeedMessage()
        feed.ParseFromString(response.content)

        vozila = []

        for entity in feed.entity:
            if entity.HasField('vehicle'):
                v = entity.vehicle
                
                lat = v.position.latitude if v.HasField('position') else None
                lon = v.position.longitude if v.HasField('position') else None
                
                if lat and lon:
                    linija = v.trip.route_id if v.HasField('trip') else "N/A"
                    vehicle_id = v.vehicle.id if (v.HasField('vehicle') and v.vehicle.id) else entity.id
                    brzina_kmh = round(v.position.speed * 3.6, 1) if (v.HasField('position') and v.position.HasField('speed')) else 0

                    vozila.append({
                        "id": str(vehicle_id),
                        "lat": lat,
                        "lon": lon,
                        "linija": str(linija),
                        "brzina": f"{brzina_kmh} km/h",
                        "tip": "tram" if len(str(linija)) <= 2 else "bus"
                    })

        return jsonify(vozila)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
