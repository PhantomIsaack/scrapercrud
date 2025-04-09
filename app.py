from flask import Flask, render_template, request, redirect, url_for
import psycopg2
import subprocess
import re  

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

    # Obtener productos de la tabla principal
    cur.execute('SELECT * FROM productos;')
    productos = cur.fetchall()

    # Obtener las tablas creadas dinámicamente
    cur.execute("""
        SELECT table_name FROM information_schema.tables 
        WHERE table_schema = 'public' AND table_name NOT IN ('productos');
    """)
    tablas = [tabla[0] for tabla in cur.fetchall()]  # Lista de nombres de tablas

    cur.close()
    conn.close()

    return render_template('index.html', productos=productos, tablas=tablas)

@app.route('/insertar/<table_name>', methods=('GET', 'POST'))
def insertar(table_name):
    if request.method == 'POST':
        titulo = request.form['titulo']
        precio = request.form['precio']
        fecha_extraccion = request.form['fecha_extraccion']
        url_producto = request.form['url']
        tienda = request.form['tienda']

        # Sanitizamos el nombre de la tabla para evitar problemas de seguridad
        table_name = sanitize_table_name(table_name)

        conn = get_db_connection()
        cur = conn.cursor()
        # Usamos el nombre de la tabla dinámicamente en la consulta
        cur.execute(
            f'INSERT INTO {table_name} (titulo, precio, fecha_extraccion, url, tienda) VALUES (%s, %s, %s, %s, %s)',
            (titulo, precio, fecha_extraccion, url_producto, tienda)
        )
        conn.commit()
        cur.close()
        conn.close()

        return redirect(url_for('mostrar_resultados', table_name=table_name))

    return render_template('insertar.html', table_name=table_name)


@app.route('/importar/amazon/<table_name>')
def importar_amazon(table_name):
    # Llamamos a amazon.py con el nombre de la tabla (que es el término de búsqueda)
    subprocess.run(['python3', 'amazon.py', table_name])
    return redirect(url_for('mostrar_resultados', table_name=table_name))

@app.route('/importar/liverpool/<table_name>')
def importar_liverpool(table_name):
    subprocess.run(["python3", "liverpool.py", table_name])
    return redirect(url_for('mostrar_resultados', table_name=table_name))


@app.route('/eliminar_datos/<table_name>')
def eliminar_datos(table_name):
    # Sanitizar el nombre de la tabla
    table_name = sanitize_table_name(table_name)
    conn = get_db_connection()
    cur = conn.cursor()
    # Ejecutar la eliminación de los datos de la tabla
    cur.execute(f'DELETE FROM {table_name};')
    conn.commit()
    cur.close()
    conn.close()
    return redirect(url_for('mostrar_resultados', table_name=table_name))

# Función para sanitizar el nombre de la tabla
def sanitize_table_name(search_term):
    return re.sub(r'[^a-zA-Z0-9_]', '', search_term.lower().replace(" ", "_"))

# Nueva ruta para la búsqueda
@app.route('/buscar', methods=['POST'])
def buscar():
    search_term = request.form['busqueda']  # Obtiene la búsqueda del formulario
    table_name = sanitize_table_name(search_term)  # Sanitiza el nombre de la tabla
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Crear la tabla si no existe
    create_table_query = f'''
    CREATE TABLE IF NOT EXISTS {table_name} (
        id SERIAL PRIMARY KEY,
        titulo VARCHAR(255),
        precio NUMERIC(10, 2),
        fecha_extraccion DATE,
        url TEXT,
        tienda VARCHAR(50)
    );
    '''
    cur.execute(create_table_query)
    conn.commit()
    
    cur.close()
    conn.close()
    
    return redirect(url_for('mostrar_resultados', table_name=table_name))

# Ruta para mostrar los resultados de la tabla creada
@app.route('/resultados/<table_name>')
def mostrar_resultados(table_name):
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        cur.execute(f'SELECT * FROM {table_name};')
        productos = cur.fetchall()
    except psycopg2.Error:
        productos = []
    
    cur.close()
    conn.close()
    
    return render_template('resultados.html', productos=productos, table_name=table_name)

# Nueva ruta para eliminar tablas
@app.route('/eliminar_tabla/<table_name>')
def eliminar_tabla(table_name):
    conn = get_db_connection()
    cur = conn.cursor()

    # Eliminar la tabla
    cur.execute(f'DROP TABLE IF EXISTS {table_name};')
    conn.commit()

    cur.close()
    conn.close()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)

    
