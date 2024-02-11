import os
import json
import subprocess
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/test', methods = ['GET', 'POST'])

def test():
    if request.method == 'GET':
        return jsonify({"response": "Get requet called"})    
    elif request.method == "POST":
        reg_json = request.json
        with open('input.json', 'w') as f:
            json.dump(reg_json, f)
            
        command = ['./json2glm', '--path-to-file', 'input.json']
        with open('input.glm','w', encoding="utf-8") as f:  
            p = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                universal_newlines=True, encoding="cp850")
            f.write(p.stdout)
            
        command = ['gridlabd', 'input.glm', '-o', 'templates/output.json']
        result = subprocess.run(command, capture_output=True, text=True)
        
        SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
        json_url = os.path.join(SITE_ROOT, "templates", "output.json")
        data = json.load(open(json_url))        
        return jsonify(data)

if __name__ == '__main__':
    app.run(debug=True)