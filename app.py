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
        r = requests.get(url, timeout=10)
        return jsonify({"vehicles": r.json()})
    except:
        return jsonify({"vehicles": []})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
