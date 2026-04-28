Instagram Scraper Masivo con Playwright
📌 Descripción

Este proyecto permite obtener información pública de perfiles de Instagram mediante automatización con Playwright y una interfaz gráfica desarrollada en Tkinter.

El sistema recopila:

Número de publicaciones
Seguidores
Seguidos
Comentarios aproximados del primer post
Fecha de extracción

Los datos se almacenan automáticamente en un archivo Excel.

⚙️ Tecnologías Utilizadas
Tecnología	Función
Python	Lenguaje principal
Tkinter	Interfaz gráfica
Playwright	Automatización del navegador
OpenPyXL	Generación de archivos Excel
JSON	Manejo de cookies
Regex	Extracción de información
📂 Estructura del Proyecto
scraping/
│
├── scrap.py
├── secret.json
├── instagram_masivo.xlsx
└── README.md
🚀 Instalación
1. Instalar Python

Descargar Python desde:

https://www.python.org/

2. Crear entorno virtual
python -m venv envc

Activar entorno:

Windows
envc\Scripts\activate
3. Instalar dependencias
pip install playwright openpyxl
4. Instalar navegadores Playwright
playwright install
🍪 Configuración de Cookies

Para evitar bloqueos de Instagram es necesario exportar cookies reales desde el navegador.

Pasos
Abrir Instagram e iniciar sesión.
Instalar la extensión Cookie-Editor.
Exportar cookies en formato JSON.
Guardar el archivo como:
secret.json
Colocar el archivo en la misma carpeta de scrap.py.
▶️ Ejecución
python scrap.py
📊 Funcionamiento General

El programa:

Abre un navegador automatizado.
Carga cookies de sesión.
Accede a perfiles públicos de Instagram.
Obtiene estadísticas visibles.
Extrae comentarios del primer post.
Guarda los resultados en Excel.
