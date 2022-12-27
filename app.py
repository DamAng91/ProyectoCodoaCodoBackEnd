from flask import Flask 
from flask import render_template, request, redirect, url_for, flash 
from flaskext.mysql import MySQL #Conexión a BBDD
from datetime import datetime #Permitirá darle el nombre a la foto
import os #PModulo del S.O. para eliminar el archivo de la foto y colocar una nueva
from flask import send_from_directory #permite a flask acceder a las carpetas

app = Flask(__name__)

app.secret_key= "ClaveScreta"

CARPETA = os.path.join('uploads')
app.config['CARPETA'] = CARPETA

#Conexión a BBDD
mysql = MySQL()
app.config['MYSQL_DATABASE_HOST']='localhost'
app.config['MYSQL_DATABASE_USER']='root'
app.config['MYSQL_DATABASE_PASSWORD']=''
app.config['MYSQL_DATABASE_DATABASE_BD']='sistema'
mysql.init_app(app)

#Permite acceder a una carpeta 
@app.route('/uploads/<nombreFoto>')
def uploads(nombreFoto):
    return send_from_directory(app.config['CARPETA'], nombreFoto)

# Ejecuta una aplicación 
@app.route('/')
def index(): #Permite  desplegar los datos de la tabla retornando el template index.html

    sql = "SELECT * FROM `sistema`.`empleados`;"
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute(sql)
    empleados = cursor.fetchall()
    print(empleados)
    conn.commit()
    return render_template('empleados/index.html', empleados=empleados)

#Permite borrar un registro de la BBDD
@app.route('/destroy/<int:id>')
def destroy(id):
    conn = mysql.connect()
    cursor = conn.cursor()

    cursor.execute("SELECT foto FROM `sistema`.`empleados` WHERE id = %s", id) #selección de datos
    fila = cursor.fetchall() #encontramos el dato, tomamos toda la info
       
    os.remove(os.path.join(app.config['CARPETA'], fila[0][0])) #removemos la foto de la carpeta uploads

    cursor.execute("DELETE FROM `sistema`.`empleados` WHERE id=%s", (id))
    conn.commit()
    return redirect('/')

#Permite editar un registro de la BBDD
@app.route('/edit/<int:id>')
def edit(id):
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM `sistema`.`empleados` WHERE id=%s", (id))
    empleados = cursor.fetchall()
    conn.commit()
    return render_template('empleados/edit.html', empleados = empleados)

#Permite cargar los datos editados del registro de BBDD
@app.route('/update', methods=['POST'])
def update():
    _nombre = request.form['txtNombre']
    _correo = request.form['txtCorreo']
    _foto = request.files['txtFoto']
    id = request.form['txtID']

    sql = "UPDATE `sistema`.`empleados` SET `nombre`=%s, `correo`=%s WHERE id = %s;"
    datos = (_nombre, _correo, id)

    conn = mysql.connect()
    cursor = conn.cursor()

    now = datetime.now()
    tiempo = now.strftime("%Y%H%M%S")
    if _foto.filename != '':
        nuevoNombreFoto = tiempo+_foto.filename
        _foto.save("uploads/"+nuevoNombreFoto)
       
        cursor.execute("SELECT foto FROM `sistema`.`empleados` WHERE id = %s", id)
        fila = cursor.fetchall()
       
        os.remove(os.path.join(app.config['CARPETA'], fila[0][0]))
        cursor.execute("UPDATE `sistema`.`empleados` SET foto = %s WHERE id = %s", (nuevoNombreFoto, id))
        conn.commit()

    cursor.execute(sql,datos)
    conn.commit()

    return redirect('/')

#Permite mostrar por pantalla a create.html, agregar la información y la envía a la BBDD
@app.route('/create') 
def create():
    return render_template('empleados/create.html')

#Permite almacenar los datos agregados en el formulario de create.html en la BBDD y luego, redireccionar
@app.route('/store', methods=['POST'])
def storage():
    #valores que provienen del formulario create.html
    _nombre = request.form['txtNombre']
    _correo = request.form['txtCorreo']
    _foto = request.files['txtFoto']

    if _nombre == '' or _correo == '' or _foto == '':
        flash('Falta completar un datos')
        return redirect(url_for('create'))

    #Obtengo el AA-HH-MIN-SEG al subir la foto
    now = datetime.now()
    tiempo = now.strftime("%Y%H%M%S")
    #Pregunto si existe la foto si no la creo y la guardo en file "uploads"
    if _foto.filename != '':
        nuevoNombreFoto = tiempo+_foto.filename
        _foto.save("uploads/"+nuevoNombreFoto)

    sql = "INSERT INTO `sistema`.`empleados` (`id`, `nombre`, `correo`, `foto`) VALUES (NULL, %s, %s, %s);"
    datos = (_nombre, _correo, nuevoNombreFoto)
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute(sql,datos)
    conn.commit()
    return redirect('/')

if __name__=='__main__':
    app.run(debug=True)

#SECCION 4