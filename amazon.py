import sys
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
import time
import datetime
import psycopg2

# Conexión a PostgreSQL
def get_db_connection():
    conn = psycopg2.connect(
        dbname="crud_audifonos",  # Cambia a tu base de datos
        user="admin",  # Cambia a tu usuario
        password="12345678",  # Cambia a tu contraseña
        host="localhost"  # Cambia a tu host
    )
    return conn

# Obtenemos el término de búsqueda de la línea de comandos (el nombre de la tabla)
search_term = sys.argv[1]  # Tomamos el nombre de la tabla que se pasa como argumento

# Iniciamos el driver de Chrome
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
driver.maximize_window()

# Construimos la URL de búsqueda dinámicamente con el término que pasa el usuario
search_url = f'https://www.amazon.com.mx/s?k={search_term.replace(" ", "+")}'
driver.get(search_url)

# Fecha de extracción
extractionDate = str(datetime.datetime.now().date())

# Lista para controlar ID interno
e = 0
nextBtn = True

# Nombre de la tabla donde se van a insertar los productos
table_name = search_term.lower().replace(" ", "_")

# Creamos la tabla si no existe
conn = get_db_connection()
cur = conn.cursor()
cur.execute(f'''
    CREATE TABLE IF NOT EXISTS {table_name} (
        id SERIAL PRIMARY KEY,
        titulo VARCHAR(255),
        precio NUMERIC(10, 2),
        fecha_extraccion DATE,
        url TEXT,
        tienda VARCHAR(50)
    );
''')
conn.commit()

while nextBtn:
    time.sleep(3)
    productos = driver.find_elements(By.XPATH, "//*[@role='listitem']")

    for producto in productos:
        try:
            titulo_element = producto.find_element(By.XPATH, ".//*[@class='a-link-normal s-line-clamp-4 s-link-style a-text-normal']")
            precio = producto.find_element(By.XPATH, ".//*[@class='a-price-whole']")
            url = titulo_element.get_attribute('href')

            # Guardamos directamente en la base de datos en la tabla correspondiente
            cur.execute(
                f'INSERT INTO {table_name} (titulo, precio, fecha_extraccion, url, tienda) VALUES (%s, %s, %s, %s, %s)',
                (titulo_element.text, precio.text.replace(",", ""), extractionDate, url, "Amazon")
            )
            conn.commit()

            e += 1

        except Exception as ex:
            print(f"Error al procesar el producto: {ex}")
            continue

    # Comprobamos si hay una siguiente página
    next_page = driver.find_elements(By.XPATH, '//*[@id="search"]/div[1]/div[1]/div/span[1]/div[1]/div[66]/div/div/span/ul/li[4]/span/a')
    if len(next_page) > 0:
        next_page[0].click()
    else:
        nextBtn = False

driver.close()
print(f"Se insertaron {e} productos en la tabla '{table_name}' desde Amazon.")
