#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: isafuent
"""

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
        dbname="crud_audifonos",
        user="admin",
        password="12345678",
        host="localhost"
    )
    return conn
# Iniciamos el driver de Chrome
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
driver.maximize_window()

# URL inicial
driver.get('https://www.amazon.com.mx/s?k=audifonos+.')

# Fecha de extracción
extractionDate = str(datetime.datetime.now().date())

# Lista para controlar ID interno
e = 0
nextBtn = True

while nextBtn:
    time.sleep(3)
    productos = driver.find_elements(By.XPATH, "//*[@role='listitem']")

    for producto in productos:
        try:
            titulo_element = producto.find_element(By.XPATH, ".//*[@class='a-link-normal s-line-clamp-4 s-link-style a-text-normal']")
            precio = producto.find_element(By.XPATH, ".//*[@class='a-price-whole']")
            url = titulo_element.get_attribute('href')

            # Guardamos directamente en la base de datos
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute(
                'INSERT INTO productos (titulo, precio, fecha_extraccion, url, tienda) VALUES (%s, %s, %s, %s, %s)',
                (titulo_element.text, precio.text.replace(",", ""), extractionDate, url, "Amazon")
            )
            conn.commit()
            cur.close()
            conn.close()

            e += 1

        except:
            continue

    next_page = driver.find_elements(By.XPATH, '//*[@id="search"]/div[1]/div[1]/div/span[1]/div[1]/div[66]/div/div/span/ul/li[4]/span/a')
    if len(next_page) > 0:
        next_page[0].click()
    else:
        nextBtn = False

driver.close()
print(f"Se insertaron {e} productos desde Amazon en la base de datos.")