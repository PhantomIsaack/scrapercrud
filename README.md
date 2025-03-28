# 📦 CRUD de Gestión de Audífonos con Web Scraping

Este proyecto es una aplicación web construida con **Flask**, **PostgreSQL**, **Selenium** y **Python** para gestionar precios de audífonos extraídos desde **Amazon México** y **Liverpool México**.

---

## ⚙️ Tecnologías utilizadas

- Python 3
- PostgreSQL
- HTML + CSS (vanilla)

---

## 🧰 Requisitos previos

- Tener Python 3 y PostgreSQL instalados
- Tener `pip` y `psycopg2-binary` disponibles
- Instalar Google Chrome

---

## 📁 Estructura del proyecto

```
CRUD-Audifonos/
├── app.py                  # App Flask principal
├── amazonh.py              # Script de scraping para Amazon
├── liverpoolh.py           # Script de scraping para Liverpool
├── templates/              # HTMLs
│   ├── base.html
│   ├── index.html
│   └── insertar.html
├── static/
│   └── css/estilos.css
├── requirements.txt        # Dependencias del proyecto
└── README.md               # Este archivo
```

---

## 🔧 Instalación y ejecución en entorno virtual

### 1. Clonar el repositorio (si aplica)
```bash
git clone https://github.com/PHantomIsaack/scrapercrud.git
cd CRUD-Audifonos
```

### 2. Crear entorno virtual
```bash
python3 -m venv venv
source venv/bin/activate  # En Linux/Mac
```

### 3. Instalar dependencias
```bash
pip install -r requirements.txt
```

> También puedes instalar manualmente:
```bash
pip install flask psycopg2-binary selenium pandas webdriver-manager
```

### 4. Configurar base de datos PostgreSQL
```sql
-- En consola psql o pgAdmin:
CREATE DATABASE crud_audifonos;
\c crud_audifonos

CREATE TABLE productos (
    id SERIAL PRIMARY KEY,
    titulo VARCHAR(255),
    precio NUMERIC(10, 2),
    fecha_extraccion DATE,
    url TEXT,
    tienda VARCHAR(50)
);
```

### 5. Configurar credenciales en `app.py`, `amazonh.py`, y `liverpoolh.py`
```python
# Ejemplo:
conn = psycopg2.connect(
    dbname="crud_audifonos",
    user="postgres",
    password="1234",
    host="localhost"
)
```

---

## 🚀 Ejecutar la aplicación

```bash
python app.py
```

Visita en tu navegador: [http://127.0.0.1:5000](http://127.0.0.1:5000)

---

## 🧪 Funcionalidades principales

- ✅ Insertar productos manualmente
- ✅ Ver productos extraídos
- ✅ Importar productos desde Amazon y Liverpool con un clic
- ✅ Eliminar todos los productos (limpiar la tabla)

---

## 📌 Notas

- La importación con Selenium abrirá una ventana de Chrome para realizar el scraping.
- Puedes automatizar el scraping con `cron` si lo deseas.

---
