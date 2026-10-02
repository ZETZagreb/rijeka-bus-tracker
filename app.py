import os
import requests
from flask import Flask, jsonify, render_template_string
from flask_cors import CORS
from google.transit import gtfs_realtime_pb2

app = Flask(__name__)
CORS(app)

ZET_PROTOBUF_URL = "https://www.zet.hr/gtfs-rt-protobuf"
PROMETKO_URL = "https://zet.prometko.cyou/vehicles/locations"

@app.route('/')
def home():
    try:
        with open("index.html", "r", encoding="utf-8") as f:
            return render_template_string(f.read())
    except Exception as e:
        return f"Greška pri učitavanju karte: {str(e)}", 500

@app.route('/podaci')
def get_data():
    vozila = []
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

    # 1. Pokušaj sa ZET Protobuf API-jem
    try:
        res = requests.get(ZET_PROTOBUF_URL, headers=headers, timeout=8)
        if res.status_code == 200:
            feed = gtfs_realtime_pb2.FeedMessage()
            feed.ParseFromString(res.content)

            for entity in feed.entity:
                if entity.HasField('vehicle'):
                    v = entity.vehicle
                    lat = v.position.latitude if v.HasField('position') else None
                    lon = v.position.longitude if v.HasField('position') else None

                    if lat and lon:
                        linija = v.trip.route_id if (v.HasField('trip') and v.trip.route_id) else "N/A"
                        v_id = v.vehicle.id if (v.HasField('vehicle') and v.vehicle.id) else entity.id
                        brzina = round(v.position.speed * 3.6, 1) if (v.HasField('position') and v.position.HasField('speed')) else 0

                        vozila.append({
                            "id": str(v_id),
                            "lat": float(lat),
                            "lon": float(lon),
                            "linija": str(linija),
                            "brzina": f"{brzina} km/h",
                            "tip": "tram" if len(str(linija)) <= 2 and str(linija) != "N/A" else "bus"
                        })
    except Exception as e:
        print(f"ZET Protobuf greška: {e}")

    # 2. Ako Protobuf nije vratio vozila, pokušaj Prometko JSON API
    if not vozila:
        try:
            res = requests.get(PROMETKO_URL, headers=headers, timeout=8)
            if res.status_code == 200:
                data = res.json()
                raw_list = data if isinstance(data, list) else data.get("vehicles", data.get("data", []))

                for item in raw_list:
                    # Traženje koordinata pod svim mogućim nazivima
                    lat = item.get("latitude") or item.get("lat") or item.get("y")
                    lon = item.get("longitude") or item.get("lon") or item.get("lng") or item.get("x")

                    if lat and lon:
                        v_id = item.get("vehicle_id") or item.get("id") or item.get("garazni_broj") or item.get("label") or "N/A"
                        linija = item.get("line_name") or item.get("line") or item.get("route_id") or item.get("route_short_name") or "N/A"
                        brzina = item.get("speed", 0)

                        vozila.append({
                            "id": str(v_id),
                            "lat": float(lat),
                            "lon": float(lon),
                            "linija": str(linija),
                            "brzina": f"{round(float(brzina), 1)} km/h",
                            "tip": "tram" if len(str(linija)) <= 2 and str(linija) != "N/A" else "bus"
                        })
        except Exception as e:
            print(f"Prometko greška: {e}")

    return jsonify(vozila)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
