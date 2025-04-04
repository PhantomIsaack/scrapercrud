from flask import Flask, render_template, request, redirect, url_for
import psycopg2
import subprocess

app = Flask(__name__)

# Conexión a PostgreSQL
def get_db_connection():
    conn = psycopg2.connect(
        dbname="crud_audifonos",
        user="admin",
        password="12345678",
        host="localhost"
    )
    return conn

@app.route('/')
def index():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM productos;')
    productos = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('index.html', productos=productos)

@app.route('/insertar', methods=('GET', 'POST'))
def insertar():
    if request.method == 'POST':
        titulo = request.form['titulo']
        precio = request.form['precio']
        fecha_extraccion = request.form['fecha_extraccion']
        url_producto = request.form['url']
        tienda = request.form['tienda']

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            'INSERT INTO productos (titulo, precio, fecha_extraccion, url, tienda) VALUES (%s, %s, %s, %s, %s)',
            (titulo, precio, fecha_extraccion, url_producto, tienda)
        )
        conn.commit()
        cur.close()
        conn.close()

        return redirect(url_for('index'))

    return render_template('insertar.html')

@app.route('/importar/amazon')
def importar_amazon():
    subprocess.run(['python3', 'amazonh.py'])
    return redirect(url_for('index'))

@app.route('/importar/liverpool')
def importar_liverpool():
    subprocess.run(['python3', 'liverpool.py'])
    return redirect(url_for('index'))

@app.route('/eliminar-todo')
def eliminar_todo():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('DELETE FROM productos;')
    conn.commit()
    cur.close()
    conn.close()
    return redirect(url_for('index'))

#phatmooo
if __name__ == '__main__':
    app.run(debug=True)
