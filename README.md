# sim-microredes-udenar
~~~
https://github.com/arras-energy/gridlabd.git
https://github.com/NREL/glm.git 
~~~

Las anteriores librerias son repositorios en github necesarias para el funcionamiento de microrredes udenar
donde se encuentra la version HIPAS GRIDLABD proporcionada por arras-energy esencial para el trabajo por medio de una api
ya que nos permite usar archivos json, esenciales para el funcionamiento del motor de calculo

## Descarga e instalacion HIPAS GRIDLABD Mac, Windows WSL, or Ubuntu Linux

~~~
curl -sL http://install-dev.gridlabd.us/install.sh | sudo sh
~~~

no olvide lo siguiente para dar permisos al entorno virtual de lo contrario no funcionara de manera correcta

~~~
sudo chmod -R g+rwx ~root /usr/local
sudo adduser $USER root
~~~
HIPAS GRIDLABD tambien puede ser compilado desde codigo pero la instalacion se vuelve compleja cuando no se tiene el suficiente conociento sobre linux.

## Transformar documentos GLM a JSON 
dentro de esta version de gridlabd podemos transfromar documentro .GLM a .JSON de la sigiente manera

~~~
bash$ gridlabd -C filename.glm -o filename.json
bash$ python3 some-script-that-modifies-filename-json.py
bash$ gridlabd filename.json -o results.json
~~~
en caso de que la conversion de archivos no funcione puede utilizar la libreria GLM que
propocionar los archivos json2glm y glm2json que puede significar una alternativa para la conversion datos
para poder trabjar de manera correcta con la api ya que recibe archivos json de entrada

reposiotrio en github, siga las instrucciones a detalle para poder compilarlo desde su maquina.
~~~
https://github.com/NREL/glm.git 
~~~
