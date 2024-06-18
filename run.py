import os
import json
import subprocess
from flask import Flask, request, jsonify
import glm
from flask_cors import CORS

app = Flask(__name__)
CORS(app, origins='http://localhost:5173', supports_credentials=True)
CORS(app, origins='http://localhost:3000', supports_credentials=True)

@app.route('/')
def main():
    return "<p> welcome to API simulator </p>"

@app.route('/glm2json', methods = ['GET','POST'])
def glm2json():
    if request.method == 'GET':
        return jsonify({"response": "Get requet called"})    
    if request.method == 'POST':
        reg_json = request.json
        data_glm = reg_json["glm"]
        #print(data_glm)
        with open('data/input/input2.glm', 'w') as f:
            f.write(data_glm) 
        command = [ 'python', 'glm2json.py']
        result = subprocess.run(command, capture_output=True, text=True) 
        return jsonify(json.loads(result.stdout))
    
     
@app.route('/test', methods = ['GET', 'POST'])
def test():
    if request.method == 'GET':
        return jsonify({"response": "Get requet called"})    
    elif request.method == "POST":
        reg_json = request.json
        with open('data/input/input.json', 'w') as f:
            json.dump(reg_json, f)
        
        directorio = "data/input"   
        command = [ './json2glm', '--path-to-file', 'input.json']
        result = subprocess.run(command, cwd=directorio,capture_output=True, text=True)
        print(result.stdout)
        with open('data/input/intro.glm', 'w') as ff:
            ff.write(result.stdout)
        
        
        directorio = "data/raw"   
        command = [ 'gridlabd', '--config', 'config.json', '../input/intro.glm', '-o', 'output.json']
        result = subprocess.run(command, cwd=directorio,capture_output=True, text=True)
        
        SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
        json_url = os.path.join(SITE_ROOT, "data" ,"raw" ,"output.json")
        data = json.load(open(json_url))        
        return jsonify(data)

if __name__ == '__main__':
    app.run(debug=True)