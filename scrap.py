import tkinter as tk #crea interfaz gráfica
from tkinter import messagebox #muestra mensajes
from openpyxl import Workbook #crea el archivo excel
from playwright.sync_api import sync_playwright #control de navegador automático
from datetime import datetime #fecha actual
import time # simula pausas


# ---------------------------
# 🔧 LIMPIAR NÚMEROS
# ---------------------------
import re

def limpiar_numero(texto):
    texto = texto.lower().replace("seguidores", "").replace("seguidos", "").replace("publicaciones", "").strip()

    # eliminar espacios
    texto = texto.replace(" ", "")

    # caso millones (ej: 1.2m o 1,2m)
    if "m" in texto:
        num = texto.replace("m", "").replace(",", ".")
        return int(float(num) * 1_000_000)

    # caso miles (ej: 1.2k o 1,2k)
    if "k" in texto:
        num = texto.replace("k", "").replace(",", ".")
        return int(float(num) * 1_000)

    # caso miles con punto (ej: 11.121)
    texto = texto.replace(".", "").replace(",", "")

    return int(re.findall(r"\d+", texto)[0])

# ---------------------------
# 📡 OBTENER INFO (PLAYWRIGHT)
# ---------------------------
from playwright.sync_api import sync_playwright
import time

def obtener_info(usuario):
    with sync_playwright() as p:

        context = p.chromium.launch_persistent_context(
            user_data_dir="mi_instagram",
            headless=False,
            slow_mo=500
        )

        page = context.new_page()

        # 🔥 Abre Instagram
        page.goto("https://www.instagram.com/")
        time.sleep(5)  # tiempo para loguearte la primera vez

        # 🔥 Luego va al perfil
        page.goto(f"https://www.instagram.com/{usuario}/")

        page.wait_for_selector("header", timeout=60000)
        time.sleep(3)

        publicaciones = page.locator("header section ul li").nth(0).inner_text()
        seguidores = page.locator("header section ul li").nth(1).inner_text()
        seguidos = page.locator("header section ul li").nth(2).inner_text()

        return publicaciones, seguidores, seguidos

# ---------------------------
# 📊 GUARDAR EXCEL
# ---------------------------
def guardar_excel(usuario, datos):
    wb = Workbook() 
    ws = wb.active

    ws.append(["Usuario", "Posts", "Seguidores", "Seguidos", "Fecha"])
    ws.append([usuario, datos[0], datos[1], datos[2], datetime.now()])

    wb.save(f"{usuario}_datos.xlsx")


# ---------------------------
# 🎯 BOTÓN
# ---------------------------
def ejecutar():
    usuario = entry.get()

    if not usuario:
        messagebox.showwarning("Error", "Ingresa usuario")
        return

    label.config(text="Procesando...")
    ventana.update()

    datos = obtener_info(usuario) #ejecuta scraping

    if datos:
        guardar_excel(usuario, datos)
        label.config(text="✅ Completado")
        messagebox.showinfo("Listo", "Datos descargados correctamente")
    else:
        label.config(text="❌ Error")


# ---------------------------
# 🖥️ INTERFAZ
# ---------------------------
ventana = tk.Tk()
ventana.title("Instagram Scraper (Playwright)")
ventana.geometry("400x250")

tk.Label(ventana, text="Usuario de Instagram").pack(pady=10)

entry = tk.Entry(ventana)
entry.pack()

tk.Button(ventana, text="Descargar", command=ejecutar).pack(pady=10)

label = tk.Label(ventana, text="")
label.pack()
ventana.mainloop()