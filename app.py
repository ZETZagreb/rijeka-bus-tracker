import os
import requests
from flask import Flask, render_template, jsonify

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/buses/rijeka')
def get_rijeka_buses():
    url = "https://api.autotrolej.hr/api/open/v1/voznired/autobusi"
    try:
        r = requests.get(url, timeout=10)
        data = r.json()
        output = []
        for bus in data:
            output.append({
                "gbr": str(bus.get("garazniBroj", "")),
                "linija": str(bus.get("linija", "")),
                "lat": bus.get("latituda"),
                "lon": bus.get("longituda")
            })
        return jsonify({"vehicles": output})
    except:
        return jsonify({"vehicles": []})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
