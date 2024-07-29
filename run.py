import os
import re
import json
import subprocess
import logging
from flask_cors import CORS
from flask import Flask, request, jsonify, stream_with_context, Response

def modify_files(data, filePath):
    for i in data:
        if data[i]['class'] in ["multi_recorder", "recorder"]:
            nombre = data[i]['file']
            nombre = nombre.split('/')
            print()
            print(nombre[-1])
            print()
            data[i]['file'] = filePath + nombre[-1]
            
    return data

def update_glm_recorders(glm_file_path, output_directory):
    try:
        # Expandir ~ a la ruta absoluta
        output_directory = os.path.expanduser(output_directory)

        # Asegurarse de que el directorio de salida exista
        if not os.path.exists(output_directory):
            os.makedirs(output_directory)

        # Leer el contenido del archivo GLM
        with open(glm_file_path, 'r') as file:
            glm_content = file.read()

        # Definir el patrón regex
        pattern = r'(recorder\s*\){[^}]*?\bfile\b'

        # Definir la función de reemplazo
        def replace_path(match):
            # Extraer las partes capturadas
            prefix = match.group(1)  # 'file '
            original_path = match.group(2).strip()  # 'R1-12.27-1_reg_output.csv'
            # Formatear la nueva ruta con la carpeta de salida
            new_path = os.path.abspath(os.path.join(output_directory, os.path.basename(original_path)))
            # Devolver la nueva ruta
            return f'{prefix}{new_path}'

        # Realizar la sustitución en el contenido del archivo
        updated_content = re.sub(pattern, replace_path, glm_content)

        # Guardar el contenido actualizado en el mismo archivo GLM
        with open(glm_file_path, 'w') as file:
            file.write(updated_content)

    except OSError as e:
        print(f"Error al actualizar el archivo GLM: {e}")
    except Exception as e:
        print(f"Ocurrió un error: {e}")


def check_symlinks_in_directory(directory):
    try:
        for item in os.listdir(directory):
            item_path = os.path.join(directory, item)
            if os.path.islink(item_path):
                target = os.readlink(item_path)
                if os.path.exists(target):
                    print(f"{item_path} es un enlace simbólico válido que apunta a {target}.")
                else:
                    print(f"{item_path} es un enlace simbólico que apunta a un destino no válido: {target}.")
            elif os.path.isdir(item_path):
                # Llamar recursivamente para directorios
                check_symlinks_in_directory(item_path)
    except OSError as e:
        print(f"Error al verificar enlaces simbólicos: {e}")

# Uso
directory_path = "/path/to/directory"
check_symlinks_in_directory(directory_path)

        
def create_symlinks(source_dir, target_dir):
    try:
        # Asegúrate de que el directorio de destino exista
        if not os.path.exists(target_dir):
            os.makedirs(target_dir)

        # Listar todos los archivos y directorios en el directorio fuente
        for item in os.listdir(source_dir):
            source_path = os.path.join(source_dir, item)
            target_path = os.path.join(target_dir, item)
            
            if os.path.isdir(source_path):
                # Si es un directorio, primero crear el directorio en el destino
                if not os.path.exists(target_path):
                    os.makedirs(target_path)
                # Llamar recursivamente para manejar subdirectorios
                create_symlinks(source_path, target_path)
            else:
                # Crear el enlace simbólico para archivos
                if not os.path.exists(target_path):
                    os.symlink(source_path, target_path)
                
        print(f"Enlaces simbólicos creados exitosamente en {target_dir}")

    except OSError as e:
        print(f"Error al crear enlaces simbólicos: {e}")
    except Exception as e:
        print(f"Ocurrió un error: {e}")


def remove_symlinks(directory):
    try:
        for item in os.listdir(directory):
            item_path = os.path.join(directory, item)
            if os.path.islink(item_path):
                os.remove(item_path)
            elif os.path.isdir(item_path):
                remove_symlinks(item_path)
                
        print("Todos los enlaces simbólicos dentro del directorio fueron eliminados exitosamente.")

    except OSError as e:
        print(f"Error al eliminar enlaces simbólicos: {e}")
    except Exception as e:
        print(f"Ocurrió un error: {e}")


app = Flask(__name__)
CORS(app, origins='http://localhost:5173', supports_credentials=True)
CORS(app, origins='http://localhost:3000', supports_credentials=True)

# Configuración de logging
logging.basicConfig(level=logging.DEBUG)

# Aumentar el límite de tamaño de contenido
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB


@app.route('/')
def main():
    return "<p> welcome to API simulator </p>"


@app.route('/json2glm', methods = ['GET','POST'])
def json2glm():
    if request.method == 'GET':
        return jsonify({"response": "Get request called"})    
    if request.method == 'POST':
        try:
            reg_json = request.json
            with open('data/input/json2glm/input2.json', 'w') as f:
                json.dump(reg_json, f) 
                
                
            command = ['gridlabd', '-C', 'data/input/json2glm/input2.json', '-o', 'data/input/json2glm/input2.glm']
            result = subprocess.run(command, capture_output=True, text=True) 
            SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
            json_url = os.path.join(SITE_ROOT, "data", "input", "json2glm","input2.glm")
            
            if not os.path.exists(json_url):
                return jsonify({"error": "Input file not found"}), 404
            
            logging.debug(f"Attempting to load JSON from {json_url}")
            
            def generate():
                with open(json_url, 'r') as f:
                    content = f.read()
                    return json.dumps({"glm":content})                        
            return Response(stream_with_context(generate()), mimetype='application/json')
            
        except Exception as e:
            logging.error(f"Error in json2glm: {str(e)}")
            return jsonify({"error": str(e)}), 500



@app.route('/glm2json', methods = ['GET','POST'])
def glm2json():
    if request.method == 'GET':
        return jsonify({"response": "Get request called"})    
    if request.method == 'POST':
        try:
            reg_json = request.json
            data_glm = reg_json["glm"]
            with open('data/input/glm2json/input2.glm', 'w') as f:
                f.write(data_glm) 
            command = ['gridlabd', '-C', 'data/input/glm2json/input2.glm', '-o', 'data/input/glm2json/input2.json']
            result = subprocess.run(command, capture_output=True, text=True) 
            SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
            json_url = os.path.join(SITE_ROOT, "data", "input", "glm2json","input2.json")
            
            if not os.path.exists(json_url):
                return jsonify({"error": "Input file not found"}), 404
            
            logging.debug(f"Attempting to load JSON from {json_url}")
            
            def generate():
                with open(json_url, 'r') as f:
                    for line in f:
                        yield line
                        
            return Response(stream_with_context(generate()), mimetype='application/json')
            
        except Exception as e:
            logging.error(f"Error in glm2json: {str(e)}")
            return jsonify({"error": str(e)}), 500
    

    
    
    
@app.route('/test', methods = ['GET', 'POST'])
def test():
    if request.method == 'GET':
        return jsonify({"response": "Get request called"})
        
    elif request.method == "POST":
        try:
            reg_json = request.json
            id = reg_json["id"]
            reg_json = reg_json["inputData"]
            reg_json["objects"] = modify_files(reg_json["objects"], "/home/daviddiaz/Documents/react/backend-simulador/uploads/{}/records/".format(id) )
            create_symlinks("/home/daviddiaz/Documents/react/backend-simulador/uploads/{}".format(id), "data/raw")
            with open('data/input/input.json', 'w') as f:
                json.dump(reg_json, f)
            
            directorio = "data/input"   
            command = ['gridlabd', '-C', 'input.json', '-o', 'intro.glm']
            result = subprocess.run(command, cwd=directorio, capture_output=True, text=True)
            logging.debug(f"json2glm output: {result.stdout}")
            
            """
            with open('data/input/intro.glm', 'w') as ff:
                ff.write(result.stdout)
            """
                
            output_directory = "~/Documents/react/backend-simulador/uploads/{}/records".format(id)
            update_glm_recorders('data/input/intro.glm', output_directory)
                            
            try:
                directorio = "data/raw" 
                # Crear el enlace simbólico
                check_symlinks_in_directory("data/raw")
                #command = ['ln', '-s', "/home/daviddiaz/Documents/react/backend-simulador/uploads/{}/1722059864529-Current_Dump_NR.csv".format(id) , '../input']
                #resultpath = subprocess.run(command, cwd=directorio, capture_output=True, text=True, check=True)

                # Ejecutar gridlabd
                #command = ['gridlabd', '--config', 'config.json', '../input/intro.glm', '-o', 'output.json']
                command = ['gridlabd', '../input/intro.glm', '-o', 'output.json']
                result = subprocess.run(command, cwd=directorio, capture_output=True, text=True)
                logging.debug(f"json2glm output: {result.stdout}")
                
                # Eliminar el enlace simbólico
                #command = ['find', directorio,'-type', 'l', '-exec', 'rm', '{}', ';']
                #resultpath = subprocess.run(command, capture_output=True, text=True, check=True)
                
            except subprocess.CalledProcessError as e:
                logging.error(f"Error al ejecutar el comando '{e.cmd}': {e.stderr}")
            except Exception as e:
                logging.error(f"Error inesperado: {e}")
               
            
            #logging.debug(f"gridlabd output: {result.stdout}")
            
            SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
            json_url = os.path.join(SITE_ROOT, "data", "raw", "output.json")
            
            if not os.path.exists(json_url):
                return jsonify({"error": "Output file not found"}), 404
            
            logging.debug(f"Attempting to load JSON from {json_url}")
            
            def generate():
                with open(json_url, 'r') as f:
                    for line in f:
                        yield line
                        
            remove_symlinks("data/raw")
            return Response(stream_with_context(generate()), mimetype='application/json')
        
        except Exception as e:
            logging.error(f"Error in test: {str(e)}")
            return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)