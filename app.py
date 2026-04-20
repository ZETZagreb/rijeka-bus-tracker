import os
import requests
from flask import Flask, render_template, jsonify

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/buses/rijeka')
def get_rijeka_buses():
    url = "https://winter-star-9de5.kombajn.workers.dev/?autotrolej"
    try:
        # Povlačimo podatke s tvog proxy linka
        r = requests.get(url, timeout=10)
        data = r.json()
        
        output = []
        # Prolazimo kroz listu autobusa
        for bus in data:
            # Važno: prilagođeno formatu koji šalje Autotrolej/Cloudflare
            output.append({
                "garageNumber": str(bus.get("gbr", "???")),
                "name": str(bus.get("linija", "N/A")),
                "latitude": bus.get("lat"),
                "longitude": bus.get("lon"),
                "destination": str(bus.get("cilj", "N/A"))
            })
        return jsonify({"vehicles": output})
    except Exception as e:
        return jsonify({"vehicles": [], "error": str(e)})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
