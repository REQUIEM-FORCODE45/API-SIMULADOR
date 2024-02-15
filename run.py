import os
import json
import subprocess
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/')
def main():
    return "<p> welcome to API simulator </p>"

@app.route('/test', methods = ['GET', 'POST'])
def test():
    if request.method == 'GET':
        return jsonify({"response": "Get requet called"})    
    elif request.method == "POST":
        reg_json = request.json
        with open('input/data/input.json', 'w') as f:
            json.dump(reg_json, f)
            
        command = [ 'gridlabd', 'input.json', '-o', 'output.json']
        result = subprocess.run(command, capture_output=True, text=True)
        
        SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
        json_url = os.path.join(SITE_ROOT,"raw" ,"output.json")
        data = json.load(open(json_url))        
        return jsonify(data)

if __name__ == '__main__':
    app.run(debug=True)