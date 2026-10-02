import os
import requests
from flask import Flask, jsonify, render_template_string
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

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
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(PROMETKO_URL, headers=headers, timeout=10)
        
        if response.status_code != 200:
            return jsonify({"error": f"Prometko API status {response.status_code}"}), 500

        data = response.json()
        vozila = []

        raw_list = data if isinstance(data, list) else data.get("vehicles", data.get("data", []))

        for item in raw_list:
            lat = item.get("latitude") or item.get("lat")
            lon = item.get("longitude") or item.get("lon") or item.get("lng")
            
            if lat and lon:
                vehicle_id = item.get("vehicle_id") or item.get("id") or item.get("garazni_broj") or "N/A"
                linija = item.get("line_name") or item.get("line") or item.get("route_id") or "N/A"
                brzina = item.get("speed", 0)

                vozila.append({
                    "id": str(vehicle_id),
                    "lat": float(lat),
                    "lon": float(lon),
                    "linija": str(linija),
                    "brzina": f"{round(float(brzina), 1)} km/h",
                    "tip": "tram" if len(str(linija)) <= 2 and str(linija) != "N/A" else "bus"
                })

        return jsonify(vozila)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
