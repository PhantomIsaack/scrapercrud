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
driver.get('https://www.liverpool.com.mx/tienda?s=audifonos+.')

extractionDate = str(datetime.datetime.now().date())
e = 0
nextBtn = True
page_count = 1
max_pages = 2

while nextBtn and page_count <= max_pages:
    time.sleep(3)
    productos = driver.find_elements(By.XPATH, "//*[@class='m-figureCard__figure card m-plp-product-card m-card']")

    for producto in productos:
        try:
            titulo_element = producto.find_element(By.XPATH, ".//*[@class='a-card-brand']")
            precio = producto.find_element(By.XPATH, ".//*[@class='a-card-discount']")

            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute(
                'INSERT INTO productos (titulo, precio, fecha_extraccion, url, tienda) VALUES (%s, %s, %s, %s, %s)',
                (titulo_element.text, precio.text.replace(",", "").replace("$", ""), extractionDate, '', "Liverpool")
            )
            conn.commit()
            cur.close()
            conn.close()

            e += 1

        except:
            continue

    next_page = driver.find_elements(By.XPATH, '//*[@id="__next"]/main/div[2]/div[1]/div/div[4]/main/div[3]/div/nav/ul/li[8]/span')
    if len(next_page) > 0 and page_count < max_pages:
        next_page[0].click()
        page_count += 1
    else:
        nextBtn = False

driver.close()
print(f"Se insertaron {e} productos desde Liverpool en la base de datos.")
