from flask import Flask
from flask import render_template, request, redirect
import mysql.connector
import os
from flask import send_from_directory


app = Flask(__name__)

app.secret_key = "ClaveSecreta"
CARPETA = os.path.join("uploads")
app.config["CARPETA"] = CARPETA

conn = mysql.connector.connect(
    host="TPO2023.mysql.pythonanywhere-services.com",
    user="TPO2023",
    password="BD2023SOL",
    db="TPO2023$default",
)
cursor = conn.cursor()


@app.route("/uploads/<nombreFoto>")
def uploads(nombreFoto):
    return send_from_directory(app.config["CARPETA"], nombreFoto)


@app.route("/")
def index():
    sql = "SELECT * FROM empleados;"
    cursor = conn.cursor()
    cursor.execute(sql)
    empleados = cursor.fetchall()
    print(empleados)
    conn.commit()
    return render_template("empleados/index.html", empleados=empleados)


@app.route("/create")
def create():
    return render_template("empleados/create.html")


@app.route("/store", methods=["POST"])
def storage():
    _nombre = request.form["txtNombre"]
    _correo = request.form["txtCorreo"]
    _foto = request.files["txtFoto"]
    uploads_dir = os.path.join(app.root_path, "uploads")
    if not os.path.exists(uploads_dir):
        os.makedirs(uploads_dir)
    _foto.save(uploads_dir + "/" + _foto.filename)

    sql = "INSERT INTO empleados (id, nombre, correo, foto) VALUES (NULL,%s, %s,%s);"
    datos = (_nombre, _correo, _foto.filename)
    cursor = conn.cursor()
    cursor.execute(sql, datos)
    conn.commit()
    return redirect("/")


@app.route("/destroy/<int:id>")
def destroy(id):
    cursor = conn.cursor()
    cursor.execute("SELECT foto FROM empleados WHERE id=%s", (id,))
    fila = cursor.fetchall()

    if fila:
        old_photo_path = os.path.join(app.config["CARPETA"], fila[0][0])
        if os.path.exists(old_photo_path):
            os.remove(old_photo_path)

    cursor.execute("DELETE FROM `empleados` WHERE id=%s", (id,))
    conn.commit()
    return redirect("/")

@app.route("/edit/<int:id>")
def edit(id):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM empleados WHERE id=%s", (id,))
    empleados = cursor.fetchone()

    if not empleados:
        return redirect("/")

    conn.commit()
    return render_template("empleados/edit.html", empleados=empleados)


@app.route("/update", methods=["POST"])
def update():
    _nombre = request.form["txtNombre"]
    _correo = request.form["txtCorreo"]
    _foto = request.files.get("txtFoto")
    id = request.form["txtID"]

    if _foto:
        uploads_dir = os.path.join(app.root_path, "uploads")
        _foto.save(uploads_dir + "/" + _foto.filename)

    sql = "UPDATE empleados SET nombre=%s, correo=%s"

    if _foto:
        sql += ", foto=%s"
        datos = (_nombre, _correo, _foto.filename, id)
    else:
        datos = (_nombre, _correo, id)

    sql += " WHERE id=%s;"

    cursor = conn.cursor()
    cursor.execute(sql, datos)
    conn.commit()
    return redirect("/")
