import tkinter as tk #genera interfaz gráfica
from tkinter import messagebox #mensajes emergentes
from openpyxl import Workbook  #crear archivos excel
from playwright.sync_api import sync_playwright #simula ser humano
from datetime import datetime #imprime fecha 
import time
import re

# ---------------------------
# 🔧 LIMPIAR NÚMEROS
# ---------------------------
def limpiar_numero(texto):
    texto = texto.lower()
    texto = texto.replace("seguidores", "").replace("seguidos", "").replace("publicaciones", "")
    texto = texto.replace("\xa0", "").replace(" ", "")

    if "m" in texto:
        num = texto.replace("m", "").replace(",", ".")
        return int(float(num) * 1_000_000)

    if "mil" in texto:
        num = texto.replace("mil", "").replace(",", ".")
        return int(float(num) * 1_000)

    if "k" in texto:
        num = texto.replace("k", "").replace(",", ".")
        return int(float(num) * 1_000)

    texto = texto.replace(".", "").replace(",", "")
    return int("".join(filter(str.isdigit, texto)))


# ---------------------------
# 📡 OBTENER INFO (SIN LOGIN)
# ---------------------------
def obtener_info(page, usuario):
    try:
        url = f"https://www.instagram.com/{usuario}/"
        page.goto(url, timeout=60000)

        # 🔥 esperar a que cargue el perfil
        page.wait_for_selector("header", timeout=15000)
        time.sleep(2)

        # 🔥 detectar bloqueo/login
        if "login" in page.url:
            print(f"❌ {usuario}: bloqueado por Instagram")
            return None

        # 🔥 obtener datos visibles
        publicaciones_txt = page.locator("header section ul li").nth(0).inner_text()
        seguidores_txt = page.locator("header section ul li").nth(1).inner_text()
        seguidos_txt = page.locator("header section ul li").nth(2).inner_text()

        publicaciones = limpiar_numero(publicaciones_txt)
        seguidores = limpiar_numero(seguidores_txt)
        seguidos = limpiar_numero(seguidos_txt)

        print(f"✅ {usuario}: OK")
        return publicaciones, seguidores, seguidos

    except Exception as e:
        print(f"❌ {usuario}: error {e}")
        return None


# ---------------------------
# 📊 SCRAPER MASIVO
# ---------------------------
def scrapear_usuarios(lista_usuarios):
    resultados = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)  # 🔥 visible = menos bloqueo

        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120 Safari/537.36",
            viewport={"width": 1280, "height": 800},
            locale="es-ES"
        )

        page = context.new_page()

        for usuario in lista_usuarios:
            usuario = usuario.strip()

            if not usuario:
                continue

            datos = obtener_info(page, usuario)

            if datos:
                resultados.append([usuario, datos[0], datos[1], datos[2]])
            else:
                resultados.append([usuario, "ERROR", "ERROR", "ERROR"])

            time.sleep(3)  # 🔥 anti-bloqueo real

        browser.close()

    return resultados


# ---------------------------
# 📊 GUARDAR EXCEL
# ---------------------------
def guardar_excel_masivo(resultados):
    wb = Workbook()
    ws = wb.active

    ws.append(["Usuario", "Posts", "Seguidores", "Seguidos", "Fecha"])

    for fila in resultados:
        ws.append(fila + [datetime.now()])

    wb.save("instagram_masivo.xlsx")


# ---------------------------
# 🎯 BOTÓN
# ---------------------------
def ejecutar():
    texto = entry.get("1.0", tk.END)

    usuarios = re.split(r"[,\n]+", texto)

    if not any(u.strip() for u in usuarios):
        messagebox.showwarning("Error", "Ingresa al menos un usuario")
        return

    label.config(text="Procesando...")
    ventana.update()

    resultados = scrapear_usuarios(usuarios)

    guardar_excel_masivo(resultados)

    label.config(text="✅ Completado")
    messagebox.showinfo("Listo", "Datos descargados correctamente")


# ---------------------------
# 🖥️ INTERFAZ
# ---------------------------
ventana = tk.Tk()
ventana.title("Instagram Scraper Masivo")
ventana.geometry("400x300")

tk.Label(ventana, text="Usuarios (uno por línea o separados por coma)").pack(pady=10)

entry = tk.Text(ventana, height=6)
entry.pack()

tk.Button(ventana, text="Descargar", command=ejecutar).pack(pady=10)

label = tk.Label(ventana, text="")
label.pack()

ventana.mainloop()