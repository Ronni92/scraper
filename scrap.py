# =========================================================
# 📦 IMPORTACIONES
# =========================================================

import tkinter as tk                         # genera interfaz gráfica
from tkinter import messagebox              # mensajes emergentes

from openpyxl import Workbook               # crear archivos excel
from playwright.sync_api import sync_playwright

from datetime import datetime               # fecha actual

import time
import re
import json


# =========================================================
# 🍪 CARGAR COOKIES
# =========================================================

def cargar_cookies(context):

    try:

        with open("secret.json", "r", encoding="utf-8") as f:

            data = json.load(f)

        # si el json tiene {"cookies":[...]}
        if isinstance(data, dict) and "cookies" in data:

            cookies = data["cookies"]

        # si el json ya es una lista
        elif isinstance(data, list):

            cookies = data

        else:

            raise Exception("Formato inválido de cookies")

        context.add_cookies(cookies)

        print("✅ Cookies cargadas correctamente")

    except Exception as e:

        print(f"❌ Error cargando cookies: {e}")

# =========================================================
# 🔧 LIMPIAR NÚMEROS
# =========================================================

def limpiar_numero(texto):

    texto = texto.lower()

    texto = (
        texto.replace("seguidores", "")
        .replace("seguidos", "")
        .replace("publicaciones", "")
        .replace("posts", "")
    )

    texto = texto.replace("\xa0", "")
    texto = texto.replace(" ", "")

    # millones
    if "m" in texto:

        num = texto.replace("m", "").replace(",", ".")

        return int(float(num) * 1_000_000)

    # miles
    if "mil" in texto:

        num = texto.replace("mil", "").replace(",", ".")

        return int(float(num) * 1_000)

    # k
    if "k" in texto:

        num = texto.replace("k", "").replace(",", ".")

        return int(float(num) * 1_000)

    texto = texto.replace(".", "").replace(",", "")

    numeros = "".join(filter(str.isdigit, texto))

    return int(numeros) if numeros else 0


# =========================================================
# 💬 OBTENER COMENTARIOS
# =========================================================

def obtener_comentarios(page):

    try:

        # buscar publicaciones
        publicaciones = page.locator("article a")

        if publicaciones.count() == 0:
            return "No disponible"

        # obtener link del primer post
        href = publicaciones.first.get_attribute("href")

        if not href:
            return "No disponible"

        # guardar url perfil
        perfil_url = page.url

        # abrir post
        post_url = f"https://www.instagram.com{href}"

        page.goto(post_url)

        time.sleep(5)

        # obtener html
        html = page.content()

        # buscar comentarios en json interno
        patron = r'"edge_media_preview_comment":{"count":(\d+)'

        resultado = re.search(patron, html)

        if resultado:

            comentarios = int(resultado.group(1))

        else:

            comentarios = 0

        # regresar perfil
        page.goto(perfil_url)

        time.sleep(3)

        return comentarios

    except Exception as e:

        print(f"⚠️ Error comentarios: {e}")

        return "No disponible"
# =========================================================
# 📡 OBTENER INFORMACIÓN
# =========================================================

def obtener_info(page, usuario):

    try:

        url = f"https://www.instagram.com/{usuario}/"

        page.goto(url, timeout=60000)

        time.sleep(8)

        # verificar login
        if "login" in page.url:

            print(f"❌ {usuario}: Instagram pidió login")

            return None

        # esperar contadores visibles
        page.wait_for_selector("header section")

        time.sleep(3)

        # obtener textos visibles
        texto = page.locator("header").inner_text()

        # buscar números
        numeros = re.findall(r'[\d.,]+', texto)

        if len(numeros) < 3:

            print(f"❌ {usuario}: no se encontraron datos")

            return None

        publicaciones = limpiar_numero(numeros[0])
        seguidores = limpiar_numero(numeros[1])
        seguidos = limpiar_numero(numeros[2])

# comentarios
        comentarios = obtener_comentarios(page)

        print(f"✅ {usuario}: OK")

        return (
            publicaciones,
            seguidores,
            seguidos,
            comentarios
        )

    except Exception as e:

        print(f"❌ {usuario}: {e}")

        return None

# =========================================================
# 📊 SCRAPER MASIVO
# =========================================================

def scrapear_usuarios(lista_usuarios):

    resultados = []

    with sync_playwright() as p:

        browser = p.chromium.launch(
            headless=False,
            slow_mo=1200
        )

        context = browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 Chrome/120 Safari/537.36"
            ),
            viewport={"width": 1280, "height": 800},
            locale="es-ES"
        )

        # cargar cookies
        cargar_cookies(context)

        # crear página
        page = context.new_page()

        page.add_init_script("""
Object.defineProperty(navigator, 'webdriver', {
    get: () => undefined
})
""")

        # abrir instagram
        page.goto("https://www.instagram.com/")

        time.sleep(5)

        page.set_default_timeout(60000)

        # recorrer usuarios
        for usuario in lista_usuarios:

            usuario = usuario.strip()

            if not usuario:
                continue

            datos = obtener_info(page, usuario)

            # guardar datos
            if datos:

                resultados.append([
                    usuario,
                    datos[0],   # publicaciones
                    datos[1],   # seguidores
                    datos[2],   # seguidos
                    datos[3]    # comentarios
                ])

            else:

                resultados.append([
                    usuario,
                    "ERROR",
                    "ERROR",
                    "ERROR",
                    "ERROR"
                ])

            # pausa anti bloqueo
            time.sleep(4)

        browser.close()

    return resultados


# =========================================================
# 📊 GUARDAR EXCEL
# =========================================================

def guardar_excel_masivo(resultados):

    wb = Workbook()

    ws = wb.active

    ws.title = "Instagram Data"

    # encabezados
    ws.append([
        "Usuario",
        "Posts",
        "Seguidores",
        "Seguidos",
        "Comentarios",
        "Fecha"
    ])

    # datos
    for fila in resultados:

        ws.append(
            fila + [datetime.now().strftime("%Y-%m-%d %H:%M:%S")]
        )

    # ancho columnas
    columnas = ["A", "B", "C", "D", "E", "F"]

    for col in columnas:

        ws.column_dimensions[col].width = 20

    # guardar excel
    wb.save("instagram_masivo.xlsx")


# =========================================================
# 🎯 EJECUTAR BOTÓN
# =========================================================

def ejecutar():

    texto = entry.get("1.0", tk.END)

    usuarios = re.split(r"[,\n]+", texto)

    # validar usuarios
    if not any(u.strip() for u in usuarios):

        messagebox.showwarning(
            "Error",
            "Ingresa al menos un usuario"
        )

        return

    # mensaje interfaz
    label.config(text="⏳ Procesando...")

    ventana.update()

    # scrapear
    resultados = scrapear_usuarios(usuarios)

    # guardar excel
    guardar_excel_masivo(resultados)

    # mensaje final
    label.config(text="✅ Completado")

    messagebox.showinfo(
        "Listo",
        "Datos descargados correctamente"
    )


# =========================================================
# 🖥️ INTERFAZ GRÁFICA
# =========================================================

ventana = tk.Tk()

ventana.title("Instagram Scraper Masivo")

ventana.geometry("500x350")


# texto
tk.Label(
    ventana,
    text="Usuarios (uno por línea o separados por coma)"
).pack(pady=10)


# caja de texto
entry = tk.Text(
    ventana,
    height=8,
    width=50
)

entry.pack()


# botón
tk.Button(
    ventana,
    text="Descargar",
    command=ejecutar
).pack(pady=15)


# estado
label = tk.Label(
    ventana,
    text=""
)

label.pack()


# iniciar ventana
ventana.mainloop()