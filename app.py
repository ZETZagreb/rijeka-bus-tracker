import os
import requests
from flask import Flask, render_template, jsonify

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/buses/rijeka')
def get_rijeka_buses():
    # Pokušat ćemo povući podatke, ali ako zapne, aplikacija se neće srušiti
    url = "https://servisi.rijeka.hr/gtfs/vehicle_positions.pb"
    try:
        r = requests.get(url, timeout=5)
        # Ako ovaj URL zahtijeva GTFS dekoder koji ti baca 127, 
        # privremeno ćemo poslati praznu listu da karta barem ostane živa
        return jsonify({"vehicles": []}) 
    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
