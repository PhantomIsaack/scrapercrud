import sys
import time
import datetime
import psycopg2
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By

# Verificar si el usuario proporcionó el nombre de la tabla
if len(sys.argv) < 2:
    print("Error: Debes proporcionar el nombre de la tabla como argumento.")
    sys.exit(1)

# Nombre de la tabla desde los argumentos
table_name = sys.argv[1]
search_query = table_name.replace("_", "+")
search_url = f'https://www.liverpool.com.mx/tienda?s={search_query}'

print(f" Buscando productos en: {search_url}")

# Función para conectar a PostgreSQL
def get_db_connection():
    try:
        conn = psycopg2.connect(
            dbname="crud_audifonos",
            user="admin",
            password="12345678",
            host="localhost"
        )
        return conn
    except Exception as e:
        print(f" Error al conectar con la base de datos: {e}")
        sys.exit(1)

# Conectar a la base de datos y crear la tabla si no existe
conn = get_db_connection()
cur = conn.cursor()
cur.execute(f'''
    CREATE TABLE IF NOT EXISTS {table_name} (
        id SERIAL PRIMARY KEY,
        titulo TEXT,
        precio NUMERIC,
        fecha_extraccion DATE,
        url TEXT,
        tienda TEXT
    );
''')
conn.commit()

# Iniciar Selenium y abrir la URL
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
driver.maximize_window()
driver.get(search_url)

# Fecha actual
extractionDate = str(datetime.datetime.now().date())

# Variables de control
insertados = 0
nextBtn = True
page_count = 1
max_pages = 2  # Puedes ajustar esto

while nextBtn and page_count <= max_pages:
    time.sleep(3)

    productos = driver.find_elements(By.XPATH, "//li[contains(@class, 'm-product__card')]")
    print(f"Página {page_count}: {len(productos)} productos encontrados")

    for producto in productos:
        try:
            url = producto.find_element(By.XPATH, ".//a").get_attribute('href')
            titulo = producto.find_element(By.XPATH, ".//figcaption//h3").text.strip()
            precio_element = producto.find_element(By.XPATH, ".//p[2]")

            precio_texto = precio_element.text.replace("$", "").replace(",", "").strip()
            precio = float(precio_texto) / 100.0

            print(f" Insertando: {titulo} - ${precio}")

            cur.execute(
                f'INSERT INTO {table_name} (titulo, precio, fecha_extraccion, url, tienda) VALUES (%s, %s, %s, %s, %s)',
                (titulo, precio, extractionDate, url, "Liverpool")
            )
            conn.commit()
            insertados += 1
        except Exception as ex:
            print(f" Error al procesar un producto: {ex}")
            continue

    # Siguiente página
    try:
        next_button = driver.find_element(By.XPATH, "//li[@class='page-item']/a[@class='page-link']")
        next_button.click()
        page_count += 1
    except Exception:
        print(" No se encontró botón de siguiente página.")
        nextBtn = False

# Cierre
cur.close()
conn.close()
driver.quit()
print(f" Se insertaron {insertados} productos en la tabla '{table_name}' desde Liverpool.")