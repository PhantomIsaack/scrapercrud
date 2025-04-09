import sys
import time
import datetime
import psycopg2
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By

#Verificar si el usuario proporcionó el nombre de la tabla
if len(sys.argv) < 2:
    print("Error: Debes proporcionar el nombre de la tabla como argumento.")
    sys.exit(1)

# Nombre de la tabla desde los argumentos
table_name = sys.argv[1]
search_query = table_name.replace("_", "+")  # Convertir "_" en "+" para la URL de búsqueda
search_url = f'https://www.liverpool.com.mx/tienda?s={search_query}'

print(f"Buscando productos en: {search_url}")

#Función para conectar a PostgreSQL
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
        print(f"Error al conectar con la base de datos: {e}")
        sys.exit(1)

#Iniciar Selenium y abrir la URL
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
driver.maximize_window()
driver.get(search_url)

# Fecha de extracción
extractionDate = str(datetime.datetime.now().date())

# Variables de control
e = 0
nextBtn = True
page_count = 1
max_pages = 2  # Limite de páginas a recorrer

while nextBtn and page_count <= max_pages:
    time.sleep(3)  # Esperar que la página cargue
    
    #Buscar productos en la página
    productos = driver.find_elements(By.XPATH, "//div[contains(@class, 'm-product__card')]")
    print(f"Página {page_count}: Se encontraron {len(productos)} productos.")

    if not productos:
        print("No se encontraron productos en esta página.")
        break  # Detener si no hay productos

    for producto in productos:
        try:
            url = producto.find_element(By.XPATH, ".//a").get_attribute('href')
            titulo_element = producto.find_element(By.XPATH, ".//h3[1]")
            precio_element = producto.find_element(By.XPATH, ".//p[contains(@class,'a-card-discount')]")

            #Limpiar el precio y convertirlo en decimal
            precio_texto = precio_element.text.replace(",", "").replace("$", "").strip()
            precio = float(precio_texto.split(" - ")[0]) if " - " in precio_texto else float(precio_texto)

            #Guardar en la tabla correspondiente
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute(
                f'INSERT INTO {table_name} (titulo, precio, fecha_extraccion, url, tienda) VALUES (%s, %s, %s, %s, %s)',
                (titulo_element.text, precio, extractionDate, url, "Liverpool")
            )
            conn.commit()
            cur.close()
            conn.close()

            e += 1
        except Exception as ex:
            print(f"Error al procesar un producto: {ex}")
            continue

    #Intentar cambiar de página
    try:
        next_page = driver.find_element(By.XPATH, "//li[@class='page-item']/a[@class='page-link']")
        next_page.click()
        print(f"➡️ Pasando a la página {page_count + 1}...")
        time.sleep(3)  # Esperar la nueva página
        page_count += 1
    except Exception:
        print("No se encontró el botón de siguiente página.")
        nextBtn = False

driver.close()
print(f"Se insertaron {e} productos desde Liverpool en la tabla '{table_name}'.")

